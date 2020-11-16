from socket import socket, AF_INET, SOCK_DGRAM
import random as rnd
import time
from Trivia import Trivia
from threading import Thread

# # # Questões # # #

trivia = Trivia()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

class Server_UDP:

    def __init__(self, server_ip, server_port):
        '''
    Inicia o processo de inicialização do servidor

    server_ip   : Endereço IP do servidor

    server_port : Número da porta a ser utilizada pelo servidor.
        '''    
        self.__server_ip = server_ip
        self.__server_port = server_port

        self.__server_socket = socket(AF_INET, SOCK_DGRAM)
        self.__server_socket.bind((server_ip, server_port))
        
        # # # # # # # # # # # # # # # # # # Criação da lista de perguntas # # # # # # # # # # # # # # # # # # 

        self.__questions_list = [trivia.get_one() for x in range(5)]
        print("Ordem das questões:")
        [print(x) for x in self.__questions_list]
        print('')

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
        self.__player_dict = {} 
        '''
Esse Dicionário de jogadores guardará as informações de todos os jogadores, formato:
ID: (<<Socket>> ,<<Nome>> ,<<Pontuação>> ,[(horário, mensagem) ,(horário, mensagem) , ... ]) # Talvez a lista de tuplas de mensagem não precise ser utilizada.

ID:
- É o Código de indentificação. Ele é gerado automaticamente pelo Cliente quando ele envia a requisição para entrar na sessão, é um número aleatório entre 1 e 10.000
Port:
- Número da Porta do client. Normalmente ele já vem junto da primeira mensagem que o cliente envia

Nome:
- Nome fornecido pelo cliente.

Pontuação:
- Quantidade de pontos feitos pelo jogador baseado em seus acertos

Horário:
- Horário em que a mensagem foi (enviada pelo cliente - / - Recebida pelo servidor ) --> a ser definido

Mensagem:
- Conteúdo da mensagem enviada pelo cliente
''' 
        
        self.__players_conected = 0 
        self.__start = False #Variável usada para começar a partida.

        # Thread do menu de controle do servidor
        control_thread = Thread(target=self.__control)
        control_thread.start()

        # Thread do método utilizado para controlar as rodadas da partida, período onde os jogadores podem oferecer suas respostas
        round_control_thread = Thread(target=self.__round_control)
        round_control_thread.start()

        # Loop de recebimento de requisições
        while self.__players_conected != 5 and not self.__start:  # O servidor só aceita pedidos para se juntar a partida enquanto o jogo não começar, ou não haverem 5 jogadores
            data, client_adress = self.__server_socket.recvfrom(2048)
            client_requisition = eval(data.decode())

            if client_requisition[0] == 'CONTROL' and client_adress == (self.__server_ip, self.__server_port): # Começa a partida caso o próprio servidor mande uma mensagem para iniciar a partida
                self.__start = True

            elif self.__players_conected >= 5:
                self.__server_socket.sendto( str(("DECLINE","FULL")).encode(), client_adress)

            
            elif client_requisition[0] not in self.__player_dict:  # Client_requisition[0] é o ID do cliente presente na tupla enviada
                print(data.decode(), client_adress) # Só está aqui para mostrar as informações do cliente, deverá ser removido posteriormente
                print(f'o jogador {client_requisition[1]} entrou na partida.')
                self.__player_dict[client_requisition[0]] = [client_adress, client_requisition[0], client_requisition[1], 0]
                
                # Inicia a Thread para envio e recebimento de resposta do cliente
                Client_thread = Thread(target=self.__client_comunication, args=(self, client_adress[0], client_adress[1], client_requisition[0]))
                Client_thread.start()
                self.__players_conected += 1

                if self.__players_conected == 5:
                    self.__start = True

            else:
                self.__server_socket.sendto( str(("DECLINE","ALREADYIN")).encode(), client_adress)
                
        return

    def __round_control(self):
        '''
        Metodo utilizado para gerenciar cada rodada de perguntas e respostas
        '''
        self.__current_question_number = 0      # Define o Numero da pergunta atual
        self.__time_over = False                # Marca o fim do tempo de respostas
        self.__round_over = False               # Marca o fim da rodada
        self.__players_answered = 0             # Registra quantos jogadores responderam à pergunta da rodada
        self.__players_answered_ID = []         # Registra todos os IDs dos jogadores que responderam as perguntas

        while not self.__start:
            time.sleep(0.1)

        ended = False
        while not ended:

            self.__players_answered = 0
            self.__round_over = False
            while not self.__round_over:
                self.__current_question = self.__questions_list[self.__current_question_number]
                # Loop de condição para fim da rodada
                self.__time_over = False
                second_counter = 0
                while self.__players_answered < self.__players_conected and not self.__time_over:
                    time.sleep(1)
                    second_counter += 1
                    print(second_counter) # # # # # Control print
                    if second_counter == 10:
                        self.__time_over = True
                        for client_ID in self.__player_dict:
                            if client_ID not in self.__players_answered_ID:
                                self.__player_dict[client_ID][3] -= 1
                
                self.__round_over = True
            self.__current_question_number += 1
            self.__players_answered = 0
            print(self.__current_question_number)

            if self.__current_question_number > 4: #4 porque o número da questão atual começa em 0
                ended = True 

        for client in self.__player_dict:
            print(self.__player_dict[client])
            end_match_tuple = ("END",'MATCH')
            self.__server_socket.sendto(str(end_match_tuple).encode(), self.__player_dict[client][0])
            time.sleep(1)
            match_results = ('RESULTS', [(self.__player_dict[x][2], self.__player_dict[x][3]) for x in self.__player_dict])
            self.__server_socket.sendto(str(match_results).encode(), self.__player_dict[client][0])

        print('A Partida acabou!')

        return

    @staticmethod
    def __send_questions(self, Client_IP, Client_Port):
        '''
        '''
        # Mensagem que marca o inicio da partida para o cliente
        start_tuple = ('START','MATCH')
        self.__server_socket.sendto(str(start_tuple).encode(), (Client_IP, Client_Port))

        # Loop de envio de perguntas e recebimento de respostas
        while self.__current_question_number < 5:
            question_to_send_number = self.__current_question_number # Pergunta enviada pela Thread
            self.__client_answered = False

            # Selecionando apenas a pergunta da rodada
            self.__question = self.__questions_list[question_to_send_number]# # # # #
            print(f'\n\n {self.__question} \n\n')

            question_tuple = ("QUESTION", question_to_send_number , self.__question[0])
            self.__server_socket.sendto(str(question_tuple).encode(), (Client_IP, Client_Port)) # Envio da pergunta

            print('Pergunta enviada:',question_tuple,'\n')
            while question_to_send_number == self.__current_question_number:
                time.sleep(0.1)

        return

    @staticmethod
    def __client_comunication(self, Client_IP, Client_Port, Client_ID):
        # Enviando a resposta para o client o informando que o servidor recebeu a mensagem e que está esperando
        authorization_and_standby = ('OK','STANDBY')
        self.__server_socket.sendto(str(authorization_and_standby).encode(), (Client_IP, Client_Port))

        while not self.__start: 
            time.sleep(0.1)
        
        # Thread para o envio de perguntas
        send_questions_thread = Thread(target=self.__send_questions, args=(self, Client_IP, Client_Port))
        send_questions_thread.start()
        self.__client_answered = False # # #

        while self.__current_question_number < 5:

            # Recebendo a resposta do Cliente
            time_over = False
            while not self.__client_answered and not time_over:

                data, client_adress = self.__server_socket.recvfrom(2048)
                client_answer =  eval(data.decode())
                print(f'O cliente {client_adress} mandou >>> {data.decode()}') # # # ##

                if client_adress == (Client_IP, Client_Port) and client_answer[0] == Client_ID and client_answer[1] == self.__current_question_number:
                    self.__players_answered += 1
                    if client_answer[2] == self.__question[1]:
                        self.__player_dict[Client_ID][3] += 25
                        self.__client_answered = True
                        self.__players_answered_ID.append(Client_ID)

                    else:
                        self.__player_dict[Client_ID][3] -= 5
                        self.__client_answered = True
                        self.__players_answered_ID.append(Client_ID)
                 
        return

    def __control(self):
        while True:
            command = input('Digite um comando: ')
            if command == '':
                None
            elif command == 'help':
                print('\nEste são os seguintes comandos:\n\n')
                print('< start >       : Inicia a sessão')
                print('< status >      : Mostra o andamento geral da sessão')
                print('< playersinfo > : Mostra as informações de cada jogador(IP, ID, Socket)\n\n')

            elif command == 'start':
                message = ('CONTROL','COMMAND')
                self.__start == True
                self.__server_socket.sendto(str(message).encode(), (self.__server_ip, self.__server_port))

            elif command == 'status':
                pass
            elif command == 'playersinfo':
                pass
            else:
                print('\nComando Inválido\n')

        pass

    # # # # # # # # # # # # # # # # # # Gets and Sets # # # # # # # # # # # # # # # # # # # # 

    def get_players_conected(self):
        return self.__players_conected
    def set_players_conected(self, value):
        self.__players_conected = value
        return

    def __get_current_question(self):
        return self.__current_question
    def __set_current_question(self, value):
        self.__current_question = value
        return

if __name__ == "__main__":
    server = Server_UDP('127.0.0.1', 9500)