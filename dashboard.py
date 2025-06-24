# Importar librerías necesarias
import dash
from dash import dcc, html  # Importación corregida
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import random

# Cargar los datos limpios
df = pd.read_csv("alojamientos_booking_limpio.csv")

# Convertir ubicación en coordenadas ficticias (si no tienes datos reales)
df["Latitud"] = df.index.map(lambda x: 40.40 + random.uniform(-0.1, 0.1))
df["Longitud"] = df.index.map(lambda x: -3.70 + random.uniform(-0.1, 0.1))

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Diseño del Dashboard
app.layout = html.Div(children=[

    html.H1(" Cuadro de Mando - Alojamientos en Madrid", style={'textAlign': 'center'}),

    # Selector de Distrito
    html.Label("🔎 Selecciona un Distrito:"),
    dcc.Dropdown(
        id='distrito-dropdown',
        options=[{'label': 'Todos', 'value': 'Todos'}] + 
                [{'label': distrito, 'value': distrito} for distrito in df["Distrito"].unique()],
        value='Todos',
        clearable=False
    ),

    # Gráficos dinámicos
    dcc.Graph(id="mapa-hoteles"),
    dcc.Graph(id="ranking-distritos"),
    dcc.Graph(id="hist-precio"),
    dcc.Graph(id="scatter-precio-puntuacion"),
    dcc.Graph(id="top-reseñas"),
    dcc.Graph(id="pie-estrellas"),
    dcc.Graph(id="top-caros"),
    dcc.Graph(id="top-puntuacion"),
    dcc.Graph(id="top-estrellas"),
])

# Callback para actualizar gráficos dinámicamente
@app.callback(
    [Output("mapa-hoteles", "figure"),
     Output("ranking-distritos", "figure"),
     Output("hist-precio", "figure"),
     Output("scatter-precio-puntuacion", "figure"),
     Output("top-reseñas", "figure"),
     Output("pie-estrellas", "figure"),
     Output("top-caros", "figure"),
     Output("top-puntuacion", "figure"),
     Output("top-estrellas", "figure")],
    [Input("distrito-dropdown", "value")]
)
def update_graphs(distrito_seleccionado):
    # Filtrar por distrito
    df_filtrado = df if distrito_seleccionado == 'Todos' else df[df["Distrito"] == distrito_seleccionado]

    # 1 **Mapa Interactivo de Alojamientos**
    fig_mapa = px.scatter_mapbox(
        df_filtrado, lat="Latitud", lon="Longitud", hover_name="Alojamiento",
        hover_data=["Precio", "Puntuación", "Estrellas", "Reseñas"],
        color="Puntuación", size="Precio", size_max=15,
        title="📍 Ubicación de Alojamientos en Madrid",
        color_continuous_scale="viridis",
        zoom=12, height=500
    )
    fig_mapa.update_layout(mapbox_style="open-street-map")

    # 2 **Ranking de Distritos por Puntuación Media**
    df_ranking = df.groupby("Distrito")["Puntuación"].mean().reset_index().sort_values(by="Puntuación", ascending=False)
    fig_ranking_distritos = px.bar(
        df_ranking, x="Puntuación", y="Distrito", orientation='h',
        title=" Ranking de Distritos con Mejores Puntuaciones",
        color="Puntuación", color_continuous_scale="plasma",
        text_auto=True
    )

    # 3️⃣ **Histograma de Precios**
    fig_hist_precio = px.histogram(
        df_filtrado, x="Precio", nbins=20, title=" Distribución de Precios",
        color_discrete_sequence=["royalblue"]
    )

    # 4️⃣ **Scatter Plot - Relación entre Puntuación y Precio**
    fig_scatter_precio = px.scatter(
        df_filtrado, x="Puntuación", y="Precio",
        title=" Relación entre Puntuación y Precio",
        color="Puntuación", color_continuous_scale="viridis"
    )

    # 5️⃣ **Top 10 Alojamientos con Más Reseñas**
    top_reviews = df_filtrado.nlargest(10, "Reseñas")
    fig_top_reviews = px.bar(
        top_reviews, x="Reseñas", y="Alojamiento", orientation='h',
        title=" Top 10 Alojamientos con Más Reseñas",
        color="Reseñas", color_continuous_scale="magma",
        text_auto=True
    )

    # 6️⃣ **Gráfico de Pastel - Distribución de Estrellas**
    fig_pie_estrellas = px.pie(
        df_filtrado, names="Estrellas", title=" Distribución de Estrellas",
        color_discrete_sequence=px.colors.sequential.Blues
    )

    # 7️⃣ **Top 10 Hoteles Más Caros**
    top_caros = df_filtrado.nlargest(10, "Precio")
    fig_top_caros = px.bar(
        top_caros, x="Precio", y="Alojamiento", orientation='h',
        title=" Top 10 Hoteles Más Caros",
        color="Precio", color_continuous_scale="reds",
        text_auto=True
    )

    # 8️⃣ **Top 10 Hoteles con Mejor Puntuación**
    top_puntuacion = df_filtrado.nlargest(10, "Puntuación")
    fig_top_puntuacion = px.bar(
        top_puntuacion, x="Puntuación", y="Alojamiento", orientation='h',
        title=" Top 10 Hoteles con Mejor Puntuación",
        color="Puntuación", color_continuous_scale="teal",
        text_auto=True
    )

    # 9️⃣ **Top 10 Hoteles con Más Estrellas**
    top_estrellas = df_filtrado.nlargest(min(10, len(df_filtrado)), "Estrellas")
    fig_top_estrellas = px.bar(
        top_estrellas, x="Estrellas", y="Alojamiento", orientation='h',
        title="✨ Top 10 Hoteles con Más Estrellas",
        color="Estrellas", color_continuous_scale="sunsetdark",
        text_auto=True
    )

    return fig_mapa, fig_ranking_distritos, fig_hist_precio, fig_scatter_precio, fig_top_reviews, fig_pie_estrellas, fig_top_caros, fig_top_puntuacion, fig_top_estrellas

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)


