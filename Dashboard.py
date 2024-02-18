import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Dash', page_icon='https://cdn-icons-png.flaticon.com/512/8133/8133832.png', layout='wide')

def formata_numero(valor, prefixo = ""):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(), 'ano':ano}

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]


## Tabelas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[
    ['Local da compra', 'lat', 'lon']
    ].merge(receita_estados,
            left_on='Local da compra',
            right_index=True).sort_values('Preço', ascending=False)

vendas_estados = pd.DataFrame(dados['Local da compra'].value_counts())
vendas_estados.columns = ['Quantidade de vendas']
vendas_estados = dados.drop_duplicates(subset='Local da compra')[
    ['Local da compra', 'lat', 'lon']
    ].merge(vendas_estados,
            left_on='Local da compra',
            right_index=True).sort_values('Quantidade de vendas', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

vendas_mensal = pd.DataFrame(dados['Data da Compra'].value_counts())
vendas_mensal.columns = ['Quantidade de vendas']
vendas_mensal = vendas_mensal.groupby(pd.Grouper(freq='M'))['Quantidade de vendas'].sum().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

receita_categorias  = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

vendas_categorias = pd.DataFrame(dados['Categoria do Produto'].value_counts())
vendas_categorias.columns = ['Quantidade de vendas']
vendas_categorias = vendas_categorias.sort_values('Quantidade de vendas', ascending=False)

# Page3
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


## Gráficos

# Page1
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title='Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0, receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title='Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title='Receita')


# Page2
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                 lat='lat',
                                 lon='lon',
                                 scope='south america',
                                 size='Quantidade de vendas',
                                 template='seaborn',
                                 hover_name='Local da compra',
                                 hover_data={'lat': False, 'lon': False},
                                 title='Quantidade de vendas por estado')

fig_vendas_mensal = px.line(vendas_mensal,
                            x='Mes',
                            y='Quantidade de vendas',
                            markers=True,
                            range_y=(0, vendas_mensal.max()),
                            color='Ano',
                            line_dash='Ano',
                            title='Vendas mensais')
fig_vendas_mensal.update_layout(yaxis_title='Vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                            x='Local da compra',
                            y='Quantidade de vendas',
                            text_auto=True,
                            title='Top estados (vendas)')
fig_receita_estados.update_layout(yaxis_title='Vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                               text_auto=True,
                               title='Quantidade de vendas por categoria')
fig_vendas_categorias.update_layout(yaxis_title='Vendas')


# Page3
def fig_receita_vendedores(qtd_vendedores):
        fig = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                     x='sum',
                     y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                     text_auto=True,
                     title=f'Top {qtd_vendedores} vendedores (receita)')
        fig.update_layout(yaxis_title='Vendedores', xaxis_title='Receita')
        return fig


def fig_vendas_vendedores(qtd_vendedores):
        fig = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                     x='count',
                     y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                     text_auto=True,
                     title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        fig.update_layout(yaxis_title='Vendedores', xaxis_title='Vendas')
        return fig


## Visualização no Streamlit
page1, page2, page3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])
with page1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)
with page2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)
with page3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_receita_vendedores(qtd_vendedores))
    with col2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_vendedores(qtd_vendedores))

