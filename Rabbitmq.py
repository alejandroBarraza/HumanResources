

# class QueueConsumer:



#     def callback(ch, method, properties, body):
#         print(" [x] %r:%r" % (method.routing_key, body))

#     connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#     channel = connection.channel()

#     channel.exchange_declare(exchange='mantencion', exchange_type='direct')

#     result = channel.queue_declare(queue='', exclusive=True)
#     queue_name = result.method.queue

#     channel.queue_bind(exchange='mantencion', queue=queue_name, routing_key="rrhh")

#     channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

#     channel.start_consuming()
