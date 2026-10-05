# Pietro Alkmin

## Tese

- Começando pela tese, quero "prever" o movimento do IBOV com base na análise de correlação com BCOM, isso vai ser metrificado principalmente por RSI, MACD, MACD signal e MACD Hist. A primeira coisa que vou fazer é definir a lógica, arquitetura, dependências, modelos e diagrama UML.

Defini que vou usar a biblioteca do Yahoo finance para comparar dois índices principais, IBOV e BCOM(Bloomberg Commodity Index) e por conta de tempo, defini que vou usar um modelo simples de tendência para calcular os indicadores.

## Arquitetura/lógica

Imagem do Excalidraw explicando a ideia, dependência, ferramentas e lógica:

![Arquitetura e lógica da solução](imagens/arquitetura-logica.png)

## Funcionamento esperado do sistema

Diagrama UML de componentes:

![Diagrama UML de componentes](imagens/uml-componentes.png)

Diagrama UML de sequência:

![Diagrama UML de sequência](imagens/uml-sequencia.png)
