from socket import socket, AF_INET, SOCK_DGRAM
import random
import time
from threading import Thread

'''
# Loop de envio de mensagens
while True:
      
    print(f'O cliente {client_adress} mandou >>> {data.decode()}')

    mensagem = input()
    self.__sock.sendto(mensagem.encode(), ('localhost', 9500))
'''
# self.__sock.close()

class Client_UDP:

    def __init__(self, name = None, server_ip = None, server_port = None):
        
        self.__sock = socket(AF_INET, SOCK_DGRAM)
        
        if name == None:
            self.__name = input("Insira o seu Nome: ")
        else:
            self.__name = name

        if server_ip == None:
            self.__server_ip = input('Insira o IP do servidor: ')
        else:
            self.__server_ip = server_ip

        if server_port == None:
            self.__server_port = int(input('Insira o número do self.__socket do servidor: '))
        else:
            self.__server_port = server_port

        self.__ID = random.randint(1,100000)
        
        # loop de conexão
        print('check 1') #####CHECK POINT 1
        server_comunication_thread = Thread(target=self.__server_comunication, args=(self, server_ip, server_port))
        server_comunication_thread.start()
        time.sleep(60)

        return

    def __waiting_response(self, server_ip, server_port):
        '''
        Função que checa se o servidor já enviou a mensagem liberando o acesso
        '''

        print('check 3') #####CHECK POINT 3
        
        counter = 1
        mensagem = 'Aguardando resposta '
        send_other_message_counter = 0

        self.__esperando_resposta = True

        while self.__esperando_resposta:

            time.sleep(0.5)

            if int(counter) == 10:
                counter = 1
                print(mensagem)
                mensagem += '.'
                if send_other_message_counter == 3:
                    requisicao = str((self.__ID, self.__name, 'CI'))
                    self.__sock.sendto(requisicao.encode(), (server_ip, server_port))
                    print('Enviando a requisição mais uma vez ao servidor')
                    send_other_message_counter = -1
                    mensagem = 'Aguardando resposta '

                send_other_message_counter+=1
                    
            counter += 0.5
        return

    @staticmethod
    def __send_answer(self, server_ip, server_port):
        while not self.__session_ended:
            answer = input('Digite a sua resposta: ')
            if answer != '':
                client_answer = str((self.__ID, self.__question_number, answer))
                self.__sock.sendto(client_answer.encode(), (server_ip, int(server_port)))
        return
    
    @staticmethod
    def __server_comunication(self, server_ip, server_port):
        '''
        Método de comunicação com o servidor
        '''

        print('check 2') #####CHECK POINT 2

        requisicao = str((self.__ID, self.__name, 'CI'))
        self.__sock.sendto(requisicao.encode(), (server_ip, server_port)) # Envio da requisição para o servidor para se juntar à partida
        print('Requisição enviada para o servidor\n\n')

        # Inicio da Thread de espera por resposta
        waiting_response_thread = Thread(target= self.__waiting_response, args=(server_ip, server_port))
        waiting_response_thread.start()
        while True:
            print('check 4') #####CHECK POINT 4
            data, server_address = self.__sock.recvfrom(2048)
            print(data.decode()) #####CHECK POINT 5
            print(server_address,' is equal to',(server_ip, server_port),'?')
            if server_address == (server_ip, server_port):
                response = eval(data.decode())
                print(response[0],response[1]) #####CHECK POINT 6
                if response[0] == 'OK' and response[1] == 'STANDBY':
                    print('O servidor aceitou sua solicitação, aguarde a primeira pergunta.\n')
                    self.__esperando_resposta = False
                    # # # Starto
                    started = False
                    while not started:
                        data, server_address = self.__sock.recvfrom(1024)
                        if server_address == (server_ip, server_port):
                            response = eval(data.decode())
                            if response[0] == 'START':
                                print('A partida irá começar!\n\n')
                                self.__session_ended = False
                                started = True
                            else:
                                pass
                        else:
                            pass
                    
                    # Thread para envio das respostas
                    answer_send_thread = Thread(target=self.__send_answer, args=(self, server_ip, server_port))
                    answer_send_thread.start()

                    while not self.__session_ended:
                        data, server_address = self.__sock.recvfrom(3072)
                        #print('Checkpoint sessions 1') ####CHECKPOINT
                        if server_address == (server_ip, server_port):
                            server_message = eval(data.decode())
                            self.__question_number = server_message[1]
                            #print('Checkpoint sessions 2') ####CHECKPOINT
                            if server_message[0] == "QUESTION":
                                print('\n',server_message[2],'\n')
                                        
                            elif server_message[0] == "END":
                                self.__session_ended = True
                            else:
                                pass
                                        
                        else:
                            pass
                    data, server_Address = self.__sock.recvfrom(3072)
                    message = eval(data.decode())
                    if message[0] == 'RESULTS':
                        print('PARTIDA ENCERRADA\n\nResultado da partida:\n\n')
                        for tuple in message[1]:
                            print(f'{tuple[0]} marcou {tuple[1]} pontos!\n')
            else:
                pass

            break
        print('- - - - FIM DA PARTIDA - - - -')
        return            

if __name__ == "__main__":
    client = Client_UDP(None,'127.0.0.1',9500)