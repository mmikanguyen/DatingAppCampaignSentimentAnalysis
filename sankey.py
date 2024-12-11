"""
File: sankey.py
Author: John Rachlin

Description: A wrapper library for plotly sankey visualizations

"""

import pandas as pd
import plotly.graph_objects as go

pd.set_option('future.no_silent_downcasting', True)


def _code_mapping(df, src, targ):
    """ Map labels in src and targ colums to integers """

    # Get the distinct labels
    labels = sorted(list(set(list(df[src]) + list(df[targ]))))

    # Create a label->code mapping
    codes = range(len(labels))
    lc_map = dict(zip(labels, codes))

    # Substitute codes for labels in the dataframe
    df = df.replace({src: lc_map, targ: lc_map})

    return df, labels



def make_sankey(df, src, targ, *cols, vals=None, **kwargs):
    """
    Create a sankey figure
    df - Dataframe
    src - Source node column
    targ - Target node column
    vals - Link values (thickness)
    """

    if vals:
        values = df[vals]
    else:
        values = [1] * len(df)

    df, labels = _code_mapping(df, src, targ)
    link = {'source': df[src], 'target': df[targ], 'value': values}

    thickness = kwargs.get("thickness", 50) # 50 is the presumed default value
    pad = kwargs.get("pad", 50)


    node = {'label': labels, 'thickness': thickness, 'pad': pad}

    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)
    fig.show()


def main():

    bio = pd.read_csv('bio.csv')
    make_sankey(bio, 'cancer', 'gene', 'evidence')


if __name__ == '__main__':
    main()

