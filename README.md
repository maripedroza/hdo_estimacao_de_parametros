<h1 align="center"> Estimação de Parâmetros - HDO de Ácido Esteárico </h1>

<p align="center">
 <a href="#descricao">Descrição do Projeto</a> •
 <a href="#comousar">Estrutura do Projeto</a>  • 
 <a href="#referencias">Referências</a>
</p>

<h2 id="descricao"> :bookmark: Descrição do Projeto </h2>

<p> 
Este projeto foi desenvolvido para o Trabalho de Conclusão de Curso da graduação em Engenharia Química na Universidade Federal do Rio de Janeiro (UFRJ). Tem como objetivo proceder a estimação de parâmetros cinéticos das reações de hidrodesoxigenação (HDO) de ácido esteárico para produção de diesel verde e a posterior simulação do processo, 
podendo ser facilmente adaptado para estudar outros modelos ou processos semelhantes. 
</p>


### Rota Reacional

<p>
Na rota reacional proposta neste trabalho para o processo de HDO de ácido esteárico (AE), a formação de hidrocarbonetos de 17 carbonos (C<sub>17</sub>) 
ocorre pela remoção direta de uma molécula de CO<sub>2</sub> através da hidrogenação do reagente. Já a formação de hidrocarbonetos de 18 carbonos (C<sub>18</sub>)
acontece primeiramente pela formação de 1-octadecanal (C<sub>18</sub>=O), seguida da hidrogenação deste a 1-octadecanol (C<sub>18</sub>OH), que por sua vez é hidrogenado
a C<sub>18</sub>, gerando moléculas de água como subproduto.
 </p>

<ul>
<li> <b> Reação 1: </b> AE + H<sub>2</sub> → C<sub>17</sub> + CO<sub>2</sub> </li>
<li> <b> Reação 2: </b> AE → C<sub>18</sub>=O - H<sub>2</sub>O </li>
<li> <b> Reação 3: </b> C<sub>18</sub>=O + H<sub>2</sub> → C<sub>18</sub>OH </li>
<li> <b> Reação 4: </b> C<sub>18</sub>OH + H<sub>2</sub> → C<sub>18</sub> - H<sub>2</sub>O <br> </li>
</ul>

### Modelos Cinéticos Avaliados

<p>
Uma vez que o processo estudado se trata de um conjunto de reações heterogêneas, que ocorrem na superfície de catalisadores sólidos, os modelos cinéticos de
Eley-Rideal e de Langmuir-Hinshelwood foram avaliados, considerando diferentes hipóteses para a etapa de adsorção.
</p>

<ul>
<li> <b> Modelo 1 (ER):</b> Modelo de Eley-Rideal, em que apenas o ácido esteárico está adsorvido no catalisador</li>
<li> <b> Modelo 2 (LH-C-ND):</b> Modelo de Langmuir-Hinshelwood considerando adsorção competitiva entre ácido esteárico e hidrogênio não-dissociado. </li>
<li> <b> Modelo 3 (LH-C-D):</b> Modelo de Langmuir-Hinshelwood considerando adsorção competitiva entre ácido esteárico e hidrogênio dissociado.</li>
<li> <b> Modelo 4 (LH-NC-D):</b> Modelo de Langmuir-Hinshelwood considerando adsorção não-competitiva entre ácido esteárico e hidrogênio dissociado.</li>
<li> <b> Modelo 5 (LH-NC-ND):</b> Modelo de Langmuir-Hinshelwood considerando adsorção não-competitiva entre ácido esteárico e hidrogênio não-dissociado.</li>
</ul>

### Estimação dos parâmetros

<p>
O procedimento de estimação de parâmetros procedeu-se de forma a minimizar o função objetivo de mínimos quadrados ponderados, 
que representa a distância entre os dados experimentais e as previsões do modelo.
Para a otimização da função, utilizou-se o método heurístico de Enxame de Partículas definindo uma região de busca, seguido do método de busca direta de Nelder Mead.
</p>

<p>
Para a análise estatística dos parâmetros, utilizou-se o método da Região de Verossimilhança com um nível de confiança de 95%
para construir os intervalos de confiança; a correlação de Pearson para avaliar a predição de cada variável dependente; e a correlação paramétrica
entre cada par de parâmetro.
 </p>

<h2 id="comousar"> 🖥️ Estrutura do Projeto </h2>

<p>
Todos os algoritmos foram desenvolvidos em linguagem <b>Python</b>. Além de algumas bibliotecas padrões da distribuição <a href="https://www.anaconda.com/products/individual">Anaconda</a>, 
também são utilizados os pacotes <a href="https://pythonhosted.org/pyswarm/">pyswarm</a> e <a href="https://pypi.org/project/numdifftools/">numdifftools</a>, 
que podem ser instalados via script da seguinte maneira: 
</p>

```python
import subprocess
subprocess.call(['pip','install','pyswarm'])
subprocess.call(['pip','install','numdifftools'])
```

O projeto é dividido em <b>4 arquivos principais</b>. <br>
<ol>
  <li> O script <i>estimacao_simulacao.py</i> é o arquivo principal, que o usuário deve executar para gerar os resultados. É onde está contido todos os procedimentos de estimação de parâmetros, análise estatística dos parâmetros e simulação do processo. 
   .
</li>

  <li> A planilha <i>dados_exp.xlsx</i>, que deve permanecer dentro da pasta <i>HDO_AE</i>, contém o <i>dataset</i> utilizado 
  para a estimação dos parâmetros. Os dados experimentais das reação de HDO de ácido esteárico
  foram extraídos dos gráficos de Arora et al. (2019) e organizados em forma de tabela. 
  </li>

  <li> O script <i>modelos.py</i>, também localizado no diretório <i>HDO_AE</i>, apresenta toda a modelagem cinética do processo. No contexto do trabalho, 
  foram estudados 5 modelos distintos a serem apresentados mais a frente na seção <a href="#teoria">Fundamentação Teórica</a>. 
  O usuário deve fazer as modificações matemáticas necessárias para avaliar outros modelos ou processos.
  </li>
  
  <li> O script <i>variaveis.py</i>, que assim como os dois arquivos anteriores deve estar na pasta <i>HDO_AE</i>, é onde o usuário define as variáveis do modelo estudado, 
  como as quantidades de experimentos analisados, variáveis independentes, variáveis dependentes e parâmetros a serem estimados.
  </li>
  
</ol>

<p>
Durante todo o procedimento de estimação e simulação são gerados tabelas, relatórios e gráficos, que são salvos em pastas específicas para cada modelo, nomeadas <i>Modelo1</i>, <i>Modelo2</i>, e assim por diante.
</p>

<h2 id="referencias"> 📜 Referências </h2>

<ul>
<li><a href="https://doi.org/10.1016/j.cej.2019.01.134"> Arora et al. (2019)</a>: artigo de onde os dados experimentais da HDO de ácido esteárico foram extraídos. </li>
<li><a href="https://doi.org/10.1109/ICNN.1995.488968"> Kennedy e Eberhart (1995)</a>: publicação original sobre a otimização por Enxame de Partículas. </li>
<li><a href="https://doi.org/10.1093/comjnl/7.4.308"> Nelder e Mead (1965)</a>: publicação original sobre o algoritmo de Nelder e Mead. </li>
<li> HILL JR, C. G; ROOT, T. W. Chapter 6. Elements of Heterogeneous Catalysis. In: <b>Introduction to Chemical Engineering Kinetics and Reactor Design.</b> 2. ed. 2014. p. 152–188.</li>
<li> SCHWAAB, M.; PINTO, J. C. <b>Análise de Dados Experimentais I</b>, 1. ed. Rio deJaneiro, E-Papers, 2007. </li>
</ul>



