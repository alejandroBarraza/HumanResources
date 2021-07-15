from Trabajador import *
from Turno import *
import sqlite3
from sqlite3 import Error
import pika
from json import loads
import threading


# connection method to database 
def create_connection(db_file):
   
    conn = None
    try:
        conn = sqlite3.connect(db_file,check_same_thread=False)
    except Error as e:
        print(e)
    return conn

def rabbitmq(conn):
    
    def insert_db_rabitmq(ch,method,properties,body):
    
        body_parse = loads(body)
        rut = body_parse["rut"]
        nombre = body_parse["nombre"]
        apellido = body_parse["apellido"] 
        horas_trabajadas =  body_parse["horas"]
        fecha = body_parse["fecha"] 

        cur = conn.cursor()
        cur.execute("""SELECT id FROM Trabajador WHERE rut = '%s'""" % rut)

        id_trabajador = "NULL"

        try:
            id_trabajador = cur.fetchone()[0]
        except:
            id_trabajador = "NULL"
            pass

        if id_trabajador == "NULL":
            print(1)
            
            cur.execute("""INSERT INTO Trabajador( rut, nombre, apellido) 
                    VALUES (?,?,?)""",( rut, nombre, apellido))

            conn.commit()
            print(2)

            cur.execute("""SELECT id FROM Trabajador WHERE rut = '%s'""" % rut)

            id_trabajador = cur.fetchone()[0]
        
        cur.execute("""INSERT INTO Turno( id_trabajador, fecha, horas_trabajadas) 
                    VALUES (?,?,?)""",( id_trabajador, fecha, horas_trabajadas))

        conn.commit()
        # ==============================================
        # incia rabbit 

    print ("iniciando rabbit")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='mantencion', exchange_type='direct')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='mantencion', queue=queue_name, routing_key="rrhh")

    channel.basic_consume(queue=queue_name, on_message_callback= insert_db_rabitmq, auto_ack=True)

    channel.start_consuming()


#select all workers
def select_all_trabajador(conn):

    cur = conn.cursor()
    cur.execute("SELECT * FROM Trabajador")
    rows = cur.fetchall()
    for row in rows:
        print(row)

def show_all_turno(conn):

    cur = conn.cursor()
    cur.execute("SELECT * FROM Turno")
    rows = cur.fetchall()
    for row in rows:
        print(row)

def show_trabajador_turno(conn, rut):

    cur = conn.cursor()
    cur.execute("""SELECT id FROM Trabajador WHERE rut = '%s'""" % rut)

    id_trabajador = cur.fetchone()[0]
    
    cur.execute("SELECT fecha, horas_trabajadas FROM Turno WHERE id_trabajador = '%s'""" % id_trabajador)
    rows = cur.fetchall()
    for row in rows:
        print(row)

def insertar_turno(conn, rut):
    

    try:

        cur = conn.cursor()
        cur.execute("""SELECT id FROM Trabajador WHERE rut = '%s'""" % rut)

        id_trabajador = cur.fetchone()[0]

        if id_trabajador == "NULL":
            return ("No existe trabajador con ese rut")

        fecha = input("ingrese fecha: ")

        horas_trabajadas = input("ingrese las horas trabajadas: ")
    
        try:
            float(horas_trabajadas)
        except:
            print("Error, horas no es un numero")
            return


        turno = Turno(id_trabajador,fecha,horas_trabajadas)

        cur.execute("""INSERT INTO Turno( id_trabajador, fecha, horas_trabajadas) 
                   VALUES (?,?,?)""",( turno.id_trabajador, turno.fecha, turno.horas_trabajadas))

        conn.commit()

        return ("Turno Insertado")

    except:
        return ("Error")

# insert a worker to Trabajador Table.
def insert_trabajador(conn):
    rut = input('Ingrese su rut: ')
    nombre = input("ingrese su nombre: ")
    apellido = input("ingrese su apellido: ")
    
    t1= Trabajador( rut, nombre, apellido)

    cur = conn.cursor()
    cur.execute("""INSERT INTO Trabajador( rut, nombre, apellido) 
                   VALUES (?,?,?)""",( t1.rut, t1.nombre, t1.apellido))
    conn.commit()
    print("El trabajador fue insertado.  ", cur.rowcount)





def menuImpreso():
    print("[1]. Ingresar un trabajador")
    print("[2]. Mostrar lista trabajadores")
    print("[3]. Agregar turno trabajador")
    print("[4]. Mostrar lista turno")
    print("[5]. Mostrar turnos trabajador")
    print("[0]. Salir del Programa")

def menu(conn):
    menuImpreso()
    option = int(input("ingresar opcion: "))
    while option != 0:
        if option == 1:
            # do something
            with conn:
                insert_trabajador(conn) 
            pass
        elif option == 2:
            with conn:
                print("1. info correspondiente a la tabla trabajador:")
                select_all_trabajador(conn)
            pass
        elif option == 3:
            with conn:
                rut = input(" Ingrese rut del trabajador: ")
                insertar_turno(conn,rut)
            pass
        elif option == 4:
            with conn:
                print("4. info correspondiente a la tabla turno:")
                show_all_turno(conn) 
        elif option == 5:
            with conn:
                rut = input("Ingrese rut del trabajdor: ")
                show_trabajador_turno(conn, rut)           
        else:
            print("selecione un numero disponible en el menu")
        print()
        menuImpreso()
        option = int(input("ingresar opcion: "))
    print("gracias por usar este programa")   
   

if __name__ == '__main__':
    database = r"C:\Users\ale\Desktop\sistemaDeRRHH\TrabajadorDB.db"
    conn = create_connection(database)

    #menu corre en segundo planos a traves de hilos y rabbit en primera linea.
    t = threading.Thread(target=menu, args=[conn])
    t.start()
    rabbitmq(conn)

    