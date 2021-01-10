"""
futurePrices, confidenceIntervalLow, confidenceIntervalHigh = GBMF(10,0.08,0.2,10,1.96)

x = list(range(len(futurePrices)))
x_rev = x[::-1]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x= x+x_rev,
    y=list(confidenceIntervalHigh)+list(confidenceIntervalLow)[::-1],
    fill='toself',
    fillcolor='rgba(0,100,80,0.2)',
    line_color='rgba(255,255,255,0)',
    showlegend=False,
    name='95% Confidence level',
))

fig.add_trace(go.Scatter(
    x=x, y=futurePrices,
    line_color='rgb(0,100,80)',
    name='Stock',
))

fig.update_traces(mode='lines')
fig.show()
"""
