class Debug():
	def imprimir_local(this, func=''):
		if func == '':
			print('[DEBUG, {}] Esperando...'.format(type(this).__name__))
		else:
			print('[DEBUG, {}, {}]'.format(type(this).__name__, func))
	imprimir_local = staticmethod(imprimir_local)

	def imprimir_mensagem(pacote):
		if type(pacote) == int:
			print('[Mensagem: {}]'.format(pacote))			
		else:
			print('[Mensagem: {} | Status: {}]'.format(pacote['mensagem'], pacote['estado_endereco']))
	imprimir_mensagem = staticmethod(imprimir_mensagem)