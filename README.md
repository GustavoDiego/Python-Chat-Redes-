# Python-Chat-Redes-
Chat UDP - Cliente

O projeto do chat foi desenvolvido em Python, utilizando o protocolo UDP para a comunicação entre clientes e um servidor. O projeto permite que cada cliente envie e receba mensagens de texto, além de compartilhar arquivos txts com outros usuários. Os scripts cliente.py e servidor.py possibilitam a conexão de usuários a uma sala de chat, permitindo o envio de mensagens de texto e o compartilhamento de arquivos.

Detalhes importantes:

•	Um socket UDP é criado para o cliente e vinculado a um endereço IP e porta local.

•	A porta local é escolhida aleatoriamente entre 8000 e 9998.

•	As mensagens podem ser de texto ou partes de um arquivo.

•	A função receber() é executada em uma thread separada para receber mensagens do servidor.

Processamento de Mensagens do Servidor:
1.	Verifica se a mensagem é fragmentada ou não.
2.	Se a mensagem for fragmentada, o servidor irá receber o código (!1!1).
3.	Caso não receba o código anterior, o servidor vai agir normalmente lendo a mensagem, criando o arquivo, salvando e printando.
4.	Caso o receba o código (!0!0!) significa que o último pedaço do arquivo foi entregue então ele salva o arquivo localmente e exibe.

Envio de Mensagens do Cliente:
1.	Loop principal para o envio de mensagens pelo cliente.
2.	Se o nome começar com "hi, meu nome eh:", o cliente envia mensagens de texto.
3.	Se o nome não começar com esse prefixo, o cliente solicita ao usuário um nome para se conectar à sala.
4.	É checado o tamanho das mensagens, e caso ela seja maior que 800 (valor escolhido com intenção de ter margem de tamanho) os arquivos serão enviados em partes, entretanto caso os arquivos sejam menor que 800 serão enviados em uma única mensagem.
