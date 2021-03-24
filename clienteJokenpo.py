import socket as sock
from constantes import *
from time import sleep
from myDebug import *

NOME_SERVIDOR = '192.168.0.7'

class ClienteJokenpon:
	def __init__(self, nome_servidor, porta_servidor):
		self.socket = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
		self.endereco_servidor = (nome_servidor, porta_servidor)
		self.estado = ForaPartida(self)

	def enviar_mensagem(self, mensagem):
		if type(mensagem) == str: 
			mensagem_byte = mensagem.encode()
		else:
			mensagem_byte = str(mensagem).encode()
		self.socket.sendto(mensagem_byte, self.endereco_servidor)

	def receber_mensagem(self):
		mensagem, endereco = self.socket.recvfrom(2048)

		if endereco == self.endereco_servidor:
			mensagem_decodificada = mensagem.decode()
			try:
				mensagem_final = int(mensagem_decodificada)
			except ValueError as error:
				mensagem_final = mensagem_decodificada
			except Exception as error:
				print(error)
		return mensagem_final

	def exibir_menu(self):
		self.estado.exibir_menu()

	def sair_programa(self):
		self.socket.close()
		print('Programa encerrado')

	def processar_mensagem(self):
		self.estado.processar_mensagem()

class EstadoCliente:
	def __init__(self, cliente):
		self.cliente = cliente

class ForaPartida(EstadoCliente):
	def __init__(self, cliente):
		EstadoCliente.__init__(self, cliente)

	def entrar_partida(self):
		Debug.imprimir_local(self, 'entrar_partida')
		self.cliente.enviar_mensagem(MSG_REQUISITAR_ENTRADA)
		self.processar_mensagem()

	def processar_mensagem(self):
		Debug.imprimir_local(self)
		mensagem = self.cliente.receber_mensagem()
		Debug.imprimir_mensagem(mensagem)
		if mensagem == MSG_ENTRADA_ACEITA:
			self.cliente.estado = EsperandoComecar(self.cliente)
			self.cliente.enviar_mensagem(MSG_ESPERANDO_COMECAR)
			self.cliente.processar_mensagem()
		elif mensagem ==  MSG_PARTIDA_LOTADA:
			print('Partida lotada.')
			self.exibir_menu()
		else:
			print('Entrada inválida.')
		self.cliente.processar_mensagem()

	def exibir_menu(self):
		print('MENU PRINCIPAL')
		print('[1] Entrar Partida')
		print('[2] Sair programa')
		entrada = input('>> ')

		if entrada == '1':
			self.entrar_partida()
		elif entrada == '2':
			self.cliente.sair_programa()
		else:
			print('Entrada inválida.')
			self.exibir_menu()

class EsperandoComecar:
	def __init__(self, cliente):
		EstadoCliente.__init__(self, cliente)

	def processar_mensagem(self):
		Debug.imprimir_local(self)
		mensagem = self.cliente.receber_mensagem()
		Debug.imprimir_mensagem(mensagem)
		if mensagem == MSG_COMECAR_PARTIDA:
			self.cliente.enviar_mensagem(MSG_PREPARADO)
			self.cliente.estado = JogandoPartida(self.cliente)
		elif mensagem == MSG_ESPERANDO_JOGADOR:
			print('Esperando jogador...')
		self.cliente.processar_mensagem()

class JogandoPartida:
	def __init__(self, cliente):
		EstadoCliente.__init__(self, cliente)
		print('Esperando para começar rodada.')

	def processar_mensagem(self):
		Debug.imprimir_local(self)
		mensagem = self.cliente.receber_mensagem()
		Debug.imprimir_mensagem(mensagem)
		if mensagem == MSG_REQUISITAR_JOGADA:
			self.cliente.estado = JogandoRodada(self.cliente)
			self.cliente.exibir_menu()
		elif mensagem == MSG_COMECAR_PARTIDA:
			self.exibir_menu()

	def exibir_menu(self):
		print('Deseja continuar? [s/n]')
		entrada = input('>> ')
		if entrada == 's':
			self.cliente.enviar_mensagem(MSG_PREPARADO)
			self.cliente.processar_mensagem()
		elif entrada == 'n':
			self.cliente.sair_programa()
		else:
			print('Entrada inválida')
			self.cliente.exibir_menu()

class JogandoRodada:
	def __init__(self, cliente):
		EstadoCliente.__init__(self, cliente)

	def fazer_jogada(self, jogada):
		self.cliente.enviar_mensagem(jogada)
		self.processar_mensagem()

	def processar_mensagem(self):
		Debug.imprimir_local(self)
		mensagem = self.cliente.receber_mensagem()
		Debug.imprimir_mensagem(mensagem)

		if mensagem in RESULTADOS:
			if mensagem == MSG_VITORIA:
				print('Você venceu.')
			elif mensagem == MSG_DERROTA:
				print('Você perdeu')
			else:
				print('Empate')
			self.cliente.estado = JogandoPartida(self.cliente)
			self.cliente.processar_mensagem()
		elif mensagem == MSG_ESPERANDO_JOGADOR:
			print('Esperando a jogada de outros jogadores')
			self.processar_mensagem()
		else:
			print('##### Mensagem ??? {}'.format(mensagem))

	def exibir_menu(self):
		print('JOGADA')
		print('[1] Pedra')
		print('[2] Papel')
		print('[3] Tesoura')
		entrada = input('>> ')

		if entrada in ('1', '2', '3'):
			self.fazer_jogada(JOGADAS[int(entrada) - 1])
		else:
			print('Entrada inválida')
			self.mostrar_menu()

if __name__ == '__main__':
	cliente = ClienteJokenpon(NOME_SERVIDOR, PORTA_SERVIDOR)
	cliente.exibir_menu()
	sleep(2)
