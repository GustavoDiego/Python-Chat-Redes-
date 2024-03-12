# Chat UDP utilizando a linguagem de programação Python
#### Um projeto da disciplina de Redes de Computadores do CIn - UFPE
#### Alunos: Alberis Alves da Silva, Arlen Ferreira da Silva Filho, Gustavo Diego da Silva, Hyan Lucas Vieira da Silva e Gleybson Ricardo Alves da Silveira 

#### O projeto do chat foi desenvolvido em Python, utilizando o protocolo UDP para a comunicação entre clientes e um servidor. O projeto permite que cada cliente envie e receba mensagens de texto. Os scripts cliente.py e servidor.py possibilitam a conexão de usuários a uma sala de chat, permitindo o envio de mensagens de texto e o compartilhamento de arquivos.



### **Chat UDP - Cliente**

Detalhes importantes:

- Um socket UDP é criado para o cliente e vinculado a um endereço IP e porta local.

- A porta local é escolhida aleatoriamente entre 8000 e 9998.

- As mensagens podem ser de texto ou partes de um arquivo.

- A função receber() é executada em uma thread separada para receber mensagens do servidor.

Processamento de Mensagens do Servidor:

1.	Verifica se a mensagem é fragmentada ou não.
2.	Se a mensagem for fragmentada, o servidor irá receber o código (!1!1).
3.	Caso não receba o código anterior, o servidor vai agir normalmente lendo a mensagem, criando o arquivo, salvando e printando.
4.	Caso o receba o código (!0!0!) significa que o último pedaço do arquivo foi entregue então ele salva o arquivo localmente e exibe.

Envio de Mensagens do Cliente:

1.	Loop principal para o envio de mensagens pelo cliente.
2.	Caso o nome começar com "hi, meu nome eh:" o cliente envia mensagens de texto.
3.	Se o nome não começar com esse prefixo, o cliente solicita novamente ao usuário um nome para se conectar à sala.
4.	É checado o tamanho das mensagens, e caso ela seja maior que 800 (valor escolhido com intenção de ter margem de tamanho) os arquivos serão enviados em partes, entretanto caso os arquivos sejam menor que 800 serão enviados em uma única mensagem.


## Segunda entrega

- Na segunda entrega, foi implementado o protocolo RTT 3.0 para garantir a confiabilidade na comunicação entre cliente e servidor. Isso envolve a utilização de números de sequência, confirmação de recebimento (acknowledgment) e retransmissão de pacotes.
- Também na segunda entrega, foram introduzidas estruturas (Structs) para empacotar e desempacotar os dados a serem enviados entre cliente e servidor, além do cálculo do checksum para garantir a integridade dos dados transmitidos.
- O código da segunda entrega implementa tratamento de erros, como a verificação de números de sequência incorretos e checksums incorretos, além de retransmissão de pacotes em caso de falhas na entrega.



### **Chat UDP - Servidor**

O código do servidor implementa a parte receptora e de broadcast do sistema de chat UDP. Ele gerencia as mensagens recebidas dos clientes, mantém uma lista de clientes conectados e distribui as mensagens para todos os participantes da sala de chat.
Funcionalidades Principais:

Configuração do Servidor:
- Um socket UDP é criado para o servidor e vinculado à porta 5555 no localhost.

Recebimento de Mensagens:
- Função executada em uma thread separada para receber mensagens dos clientes.
- As mensagens recebidas são colocadas em uma fila (mensagens).

Broadcast de Mensagens:
- Função executada em uma thread separada para distribuir as mensagens recebidas para todos os clientes.
- Mantém uma lista de clientes conectados.
- Envia a mensagem recebida para todos os clientes na lista.
- Se a mensagem contiver uma "tag_de_entrada", notifica os clientes sobre a entrada de um novo participante.


## Segunda entrega

- Assim como no código do cliente, o código do servidor da segunda entrega implementa o protocolo RTT 3.0 para garantir a confiabilidade na comunicação entre cliente e servidor. Isso inclui o uso de números de sequência, confirmações de recebimento (acknowledgments) e retransmissão de pacotes.
- Foram introduzidas estruturas (Structs) para empacotar e desempacotar os dados transmitidos entre cliente e servidor, juntamente com o cálculo do checksum para garantir a integridade dos dados.
- O código do servidor da segunda entrega inclui lógica para enviar e receber acknowledgments (ACKs) entre servidor e cliente, garantindo a entrega confiável de mensagens.
- O código implementa tratamento de erros, como verificação de números de sequência incorretos e checksums incorretos, além de retransmissão de pacotes em caso de falhas na entrega.
- Foi adicionado um timer para controlar o tempo de espera por ACKs, garantindo que os pacotes sejam retransmitidos se não houver confirmação de recebimento dentro do tempo limite.
