# Controle-Auto-Scan
Repositório de backup dos **modelos 3d desenvolvidos** e do código em **python**, do **Controle Auto Scan** para sistema automatizado de rastreamento de campo próximo.
****
#### Estrutura de atuação
A estrutura de atuação desenvolvida no software "fusion360", para levantamento de componentes e visualização do produto final.
![N|Solid](/images/IMG1.png)

Para lista de componentes clique [AQUI](https://docs.google.com/document/d/15HYgylcvzmUAGObxVd7cbkju6tUG08WlYevftHTd1gw/edit?usp=sharing) .

O controle de atuação será feito com [CNC Shield V3 para Arduino Uno](https://www.filipeflop.com/produto/cnc-shield-v3-para-arduino-impressora-3d/) com [Grbl1.1](https://github.com/grbl/grbl).
****
#### Código
O código está sendo desenvolvido na liguagem de programação **Python 3.3**.
![N|Solid](/images/IMG2.png)

![N|Solid](/images/IMG6.png)

Com as seguintes bibliotecas:
- Tkinter : Interface gráfica;
- Serial : Comunicação com Grbl1.1;
- Time : Adicionar atraso (somente para teste);
- Csv : Leitura e escrita de arquivos csv;
- Datetime : Tempo atual da máquina (pós-fixo nome da arquivo);
- Matplotlib : Gera Mapa de calor
- Numpy : Operações com vetores multidimensionais
****
#### Lista de controle 
Recursos essênciais:
- [x] Comunicação serial com GRBL1.1
- [x] Comunicação analisador de espectro HAMEG HMS-X
- [x] Geração e atualização da matriz
- [x] Definição e comunição da frequência de medição
- [x] Comando do botão de "Parar Medição"
- [x] Espaço de apresentação de parametros
- [x] Comando do botão de "Inicia Medição"
- [x] Movimento dos eixos X Y Z separadamente
- [x] Recurso para salvar arquivo
- [x] Tempo estimado da medição
- [x] Barra de progresso da medição
- [x] Botão e comando para "Home"
- [x] Escolha de ponto para remedir
- [x] Interação com código de plotagem

Após terminar os recursos essênciais:
- [x] Divisão em classes de interface, CNC e istrumento
- [ ] Organização e comentários no código
- [x] Janela expansível
