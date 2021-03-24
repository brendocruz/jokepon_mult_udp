import socket as sock
from time import sleep
from constantes import *
from myDebug import *

class ServidorJokenpo:
	def __init__(self, porta_servidor):
		self.socket = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
		self.socket.bind(('', porta_servidor))
		self.estado = EsperandoPartida(self)
		self.lista_jogadores = []

	def enviar_mensagem(self, mensagem, destino=None):
		if type(mensagem) == str: 
			mensagem_byte = mensagem.encode()
		else:
			mensagem_byte = str(mensagem).encode()

		if destino == None:
			for jogador in self.lista_jogadores:
				self.socket.sendto(mensagem_byte, jogador)
		else:
			self.socket.sendto(mensagem_byte, destino)

	def receber_mensagem(self):
		mensagem, endereco = self.socket.recvfrom(2048)

		try:
			indice_jogador = self.lista_jogadores.index(endereco)
		except ValueError as error:
			estado_endereco = ENDERECO_DESCONHECIDO
		else:
			estado_endereco = ENDERECO_CONHECIDO

		mensagem_decodificada = mensagem.decode()
		try:
			mensagem_final = int(mensagem_decodificada)
		except ValueError as error:
			mensagem_final = mensagem_decodificada

		pacote = {'mensagem': mensagem_final, 'estado_endereco': estado_endereco,
				'endereco': endereco}
		return pacote

	def adicionar_jogador(self, endereco_jogador):
		if endereco_jogador in self.lista_jogadores:
			return False
		else:
			self.lista_jogadores.append(endereco_jogador)
			return True

	def remover_jogador(self, endereco_jogador):
		if endereco_jogador not in self.lista_jogadores:
			return False
		else:
			self.lista_jogadores.remove(endereco_jogador)
			return True

	def quantidade_jogadores(self):
		return len(self.lista_jogadores)

	def processar_mensagem(self):
		print('Processando mensagem...')
		self.estado.processar_mensagem()

	def comecar_partida(self):
		self.estado.comecar_partida()

	def comecar_rodada(self):
		self.estado.comecar_rodada()

	def calcular_resultado(self, lista_jogadas):
		self.estado.calcular_resultado(lista_jogadas)

	def enviar_resultado(self):
		self.estado.enviar_resultado()

	def terminar_rodada(self):
		self.estado.terminar_rodada()

	def processar_mensagem(self):
		self.estado.processar_mensagem()

	def esperando_partida(self):
		self.estado.esperando_partida()

	def requisitar_jogada(self):
		self.estado.requisitar_jogada()

	def processar_resultado(self, resultados):
		self.estado.processar_resultado(resultados)

	def preparar_rodada(self):
		self.estado.preparar_rodada()
		pass

# END class

class EstadoServidor:
	def __init__(self, servidor):
		self.servidor = servidor

	def comecar_partida(self):
		pass

	def comecar_rodada(self):
		pass

	def calcular_resultado(self):
		pass

	def enviar_resultado(self):
		pass

	def terminar_rodada(self):
		pass

	def processar_mensagem(self):
		pass

	def preparar_rodada(self):
		pass

class EsperandoPartida(EstadoServidor):
	def __int__(self, servidor):
		EstadoServidor.__init__(self, servidor)

	def processar_mensagem(self):
		Debug.imprimir_local(self)
		pacote = self.servidor.receber_mensagem()
		Debug.imprimir_mensagem(pacote)
		if pacote['mensagem'] == MSG_REQUISITAR_ENTRADA:
			self.servidor.adicionar_jogador(pacote['endereco'])
			self.servidor.estado = EsperandoJogador(self.servidor)
			self.servidor.enviar_mensagem(MSG_ENTRADA_ACEITA)
			self.servidor.processar_mensagem()

class EsperandoJogador(EstadoServidor):
	def __init__(self, servidor):
		EstadoServidor.__init__(self, servidor)

	def processar_mensagem(self):
		Debug.imprimir_local(self)
		pacote = self.servidor.receber_mensagem()
		Debug.imprimir_mensagem(pacote)
		if pacote['estado_endereco'] == ENDERECO_DESCONHECIDO:
			if pacote['mensagem'] == MSG_REQUISITAR_ENTRADA:
				self.servidor.adicionar_jogador(pacote['endereco'])
				self.servidor.enviar_mensagem(MSG_ENTRADA_ACEITA)
				if self.servidor.quantidade_jogadores() == TOTAL_JOGADORES:
					self.servidor.estado = JogandoPartida(self.servidor)
					self.servidor.comecar_partida()
				else:
					self.servidor.processar_mensagem()
		elif pacote['estado_endereco'] == ENDERECO_CONHECIDO:
			if pacote['mensagem'] == MSG_SAIR_PARTIDA:
				self.servidor.remover_jogador(pacote['endereco'])
				if self.servidor.quantidade_jogadores() == 0:
					self.servidor.estado = EsperandoPartida(self.servidor)
			self.servidor.processar_mensagem()
	pass

class JogandoPartida(EstadoServidor):
	def __init__(self, servidor):
		EstadoServidor.__init__(self, servidor)

	def comecar_partida(self):
		Debug.imprimir_local(self, 'comecar_partida')
		for jogador in self.servidor.lista_jogadores:
			self.servidor.enviar_mensagem(MSG_COMECAR_PARTIDA, jogador)
			self.servidor.processar_mensagem()
		self.servidor.estado = JogandoRodada(self.servidor)
		self.servidor.requisitar_jogada()

	def preparar_rodada(self):
		Debug.imprimir_local(self, 'preparar_rodada')
		for jogador in self.servidor.lista_jogadores:
			self.servidor.enviar_mensagem(MSG_COMECAR_PARTIDA, jogador)
			self.servidor.processar_mensagem()
		self.servidor.estado = JogandoRodada(self.servidor)
		self.servidor.requisitar_jogada()

	def processar_mensagem(self):
		Debug.imprimir_local(self)
		pacote = self.servidor.receber_mensagem()
		Debug.imprimir_mensagem(pacote)
		if pacote['mensagem'] != MSG_PREPARADO:
			self.servidor.processar_mensagem()

class JogandoRodada(EstadoServidor):
	def __init__(self, servidor):
		EstadoServidor.__init__(self, servidor)
		self.lista_jogadas = []

	def requisitar_jogada(self):
		Debug.imprimir_local(self, 'requisitar_jogada')
		for jogador in self.servidor.lista_jogadores:
			self.servidor.enviar_mensagem(MSG_REQUISITAR_JOGADA)
			self.servidor.processar_mensagem()

		if len(self.lista_jogadas) == TOTAL_JOGADORES:
			resultados = self.calcular_resultado(self.lista_jogadas)

			self.servidor.estado = TerminandoRodada(self.servidor)
			self.servidor.processar_resultado(resultados)

	def processar_mensagem(self):
		Debug.imprimir_local(self)
		pacote = self.servidor.receber_mensagem()
		Debug.imprimir_mensagem(pacote)
		if pacote['mensagem'] in JOGADAS:
			self.lista_jogadas.append(pacote)
		elif pacote['mensagem'] == MSG_SAIR_PARTIDA:
			print('FAZER ALGO')

	def calcular_resultado(self, lista_jogadas):
		jogada1 = lista_jogadas[0]['mensagem']
		jogada2 = lista_jogadas[1]['mensagem']

		if jogada1 == jogada2:
			resultado1 = MSG_EMPATE
			resultado2 = MSG_EMPATE
		elif jogada1 == MSG_JOGADA_PAPEL:
			if jogada2 == MSG_JOGADA_PEDRA:
				resultado1 = MSG_VITORIA
				resultado2 = MSG_DERROTA
			if jogada2 == MSG_JOGADA_TESOURA:
				resultado1 = MSG_DERROTA
				resultado2 = MSG_VITORIA
		elif jogada1 == MSG_JOGADA_PEDRA:
			if jogada2 == MSG_JOGADA_TESOURA:
				resultado1 = MSG_VITORIA
				resultado2 = MSG_DERROTA
			if jogada2 == MSG_JOGADA_PAPEL:
				resultado1 = MSG_DERROTA
				resultado2 = MSG_VITORIA
		elif jogada1 == MSG_JOGADA_TESOURA:
			if jogada2 == MSG_JOGADA_PAPEL:
				resultado1 = MSG_VITORIA
				resultado2 = MSG_DERROTA
			if jogada2 == MSG_JOGADA_PEDRA:
				resultado1 = MSG_DERROTA
				resultado2 = MSG_VITORIA

		resultados_final = (
			{
			'resultado': resultado1,
			'endereco': lista_jogadas[0]['endereco']
		}, {
			'resultado': resultado2,
			'endereco': lista_jogadas[1]['endereco']
			}
		)
		return resultados_final

class TerminandoRodada(EstadoServidor):
	def __init__(self, servidor):
		EstadoServidor.__init__(self, servidor)

	def processar_resultado(self, resultados):
		Debug.imprimir_local(self, 'processar_resultado')
		for resultado in resultados:
			self.servidor.enviar_mensagem(resultado['resultado'], resultado['endereco'])
		self.servidor.estado = JogandoPartida(self.servidor)
		self.servidor.preparar_rodada()


if __name__ == '__main__':
	servidor = ServidorJokenpo(PORTA_SERVIDOR)
	servidor.processar_mensagem()
	sleep(3)