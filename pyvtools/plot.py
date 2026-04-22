from matplotlib import ticker
import matplotlib.pyplot as plt

def set_style(params=None, params_to_exclude=None):
    """Sets academic style
    
    Source: https://github.com/0xInfty/PyMeepPlasmonics/blob/master/v_plot.py
    """
    
    default_params = {'text.usetex': False, 
                      'font.family':'serif',
                      'font.sans-serif': ['MS Reference Sans Serif', 'sans-serif'], 
                      'mathtext.fontset': 'cm', # Computer Modern
                      'font.weight':500,
                      'figure.titlesize':13,
                      'axes.titlesize':12,
                      'axes.labelsize':11,
                      'legend.fontsize':11,
                      'xtick.labelsize':10,
                      'ytick.labelsize':10,
                      'xtick.minor.visible':True,
                      'ytick.minor.visible':True,
                      'grid.alpha':0.4,
                      'axes.grid':True,
                      'xtick.color':'b0b0b0',
                      'ytick.color':'b0b0b0',
                      'xtick.labelcolor':'black',
                      'ytick.labelcolor':'black',
                      'lines.markersize':8,
                      'hatch.color':'white'}
    if params is not None:
        assert isinstance(params, dict), "new_params must be a dictionary"
        new_params = {**default_params, **params}
    else:
        new_params = default_params
    if params_to_exclude is not None:
        if not (isinstance(params_to_exclude, list) or isinstance(params_to_exclude, tuple)):
            raise ValueError("params_to_exclude must be a list or a tuple")
        for param in params_to_exclude:
            new_params.pop(param)
    plt.rcParams.update(new_params)

def reset_style():
    """Resets style to default"""
    plt.rcParams.update(plt.rcParamsDefault)

def add_style(fig=None, new_figure=False, **kwargs):
    """Gives style to figures to include in Latex PDF files.
    
    This function...
        ...increases font size;
        ...increases linewidth;
        ...increases markersize;
        ...gives format to axis ticks if specified;
        ...stablishes new figure dimensions if specified;
        ...activates grid.
    
    Source: https://github.com/0xInfty/PyMeepPlasmonics/blob/master/v_plot.py

    Parameters
    ----------
    figure_id : int, optional
        ID of the figure where the text will be printed.
        If none is given, the current figure is taken as default.
    new_figure=False : bool, optional
        Indicates whether to make a new figure or not when 
        figure_id=None.
    
    Other Parameters
    ----------------
    xaxisformat : format-like str, optional.
        Used to update x axis ticks format; i.e.: '%.2e'
    yaxisformat : format-like str, optional.
        Used to update y axis ticks format; i.e.: '%.2e'
    dimensions: list with length 4, optional.
        Used to update plot dimensions: [xmin, xmax, ymin, ymax]. Each 
        one should be a number expressed as a fraction of current 
        dimensions.
    
    See Also
    --------
    matplotlib.pyplot.axis
    matplotlib.pyplot.gcf
    """
    
    if fig is None:    
        if new_figure:
            fig = plt.figure()
        else:
            fig = plt.gcf()

    try:
        ax = fig.axes
        ax[0]
    except IndexError:
        ax = [plt.axes()]
    
    kwargs_default = dict(
            fontsize=12,
            linewidth=3,
            markersize=6,
            dimensions=[1.15,1.05,1,1],
            tight_layout=True,
            grid=False,
            xaxisformat=None,
            yaxisformat=None)
    
    kwargs = {key:kwargs.get(key, value) 
              for key, value in kwargs_default.items()}
    
    plt.rcParams.update({'font.size': kwargs['fontsize']})
    plt.rcParams.update({'lines.linewidth': kwargs['linewidth']})
    plt.rcParams.update({'lines.markersize': kwargs['markersize']})
    for a in ax:
        box = a.get_position()
        a.set_position([kwargs['dimensions'][0]*box.x0,
                        kwargs['dimensions'][1]*box.y0,
                        kwargs['dimensions'][2]*box.width,
                        kwargs['dimensions'][3]*box.height])
    
    if kwargs['xaxisformat'] is not None:
        for a in ax:
            a.xaxis.set_major_formatter(ticker.FormatStrFormatter(
                kwargs['xaxisformat']))
        
    if kwargs['yaxisformat'] is not None:
        for a in ax:
            a.yaxis.set_major_formatter(ticker.FormatStrFormatter(
                kwargs['yaxisformat']))
        
    for a in ax:
        a.grid(kwargs['grid'])
        
    fig.tight_layout = kwargs['tight_layout']
    
    plt.show()

    return fig