# Controle-Auto-Scan
Repositório de backup dos **modelos 3d desenvolvidos** e do código em **python**, do **Controle Auto Scan** para sistema automatizado de rastreamento de campo próximo.
****
#### Estrutura de atuação
A estrutura de atuação desenvolvida no software "fusion360", para levantamento de componentes e visualização do produto final.
![N|Solid](/IMG/IMG1.png)
Para lista de componentes clique [AQUI](https://docs.google.com/document/d/15HYgylcvzmUAGObxVd7cbkju6tUG08WlYevftHTd1gw/edit?usp=sharing) .

O controle de atuação será feito com [CNC Shield V3 para Arduino Uno](https://www.filipeflop.com/produto/cnc-shield-v3-para-arduino-impressora-3d/) com [Grbl1.1](https://github.com/grbl/grbl).
****
#### Código
O código está sendo desenvolvido na liguagem de programação **Python 3.3**.
![N|Solid](/IMG/IMG2.png)
Com as seguintes bibliotecas:
- Tkinter : Interface gráfica;
- Serial : Comunicação com Grbl1.1;
- Time : Adicionar atraso (somente para teste);
- Openpyxl : Leitura e escrita de arquivos xlsx/xlsm;
- Datetime : Tempo atual da máquina (pós-fixo nome da arquivo);
****
#### Lista de controle 
Recursos essênciais:
- [x] Comunicação serial com GRBL1.1
- [ ] Comunicação analisador de espectro HAMEG HMS-X
- [x] Geração e atualização da matriz
- [ ] Definição e comunição da frequência de medição
- [x] Comando do botão de "Parar Medição"
- [ ] Comando do botão de "Pausar Medição"
- [x] Espaço de apresentação de parametros
- [x] Comando do botão de "Inicia Medição"
- [x] Movimento dos eixos X Y Z separadamente
- [x] Recurso para salvar arquivo
- [ ] Tempo estimado da medição
- [x] Barra de progresso da medição
- [ ] Botão e comando para "Home"
- [ ] Escolha de ponto para remedir

Após terminar os recursos essênciais:
- [ ] Divisão em classes de interface, CNC e istrumento
- [ ] Organização e comentários no código
- [ ] Interação com código de plotagem

Possíveis recursos adicionais:
- Adicionar eixo Z a medição
- Tabela alterar de cor dependendo da intensidade de campo
