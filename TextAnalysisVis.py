"""
Use of TextAnalysisLib.py - using to compare language used in Hinge vs. Tinder
"""

from TextAnalysisLib import TextAnalysisLibrary

def main():
    ta = TextAnalysisLibrary()
    ta.load_stop_words('stopwords.txt')

    # Dating App Websites
    # Hinge Campaign Link
    ta.load_text('https://hinge.co/press/No-Ordinary-Love-2024', 'Hinge Advertising', parser=ta.custom_parser)

    # Tinder Campaign Link
    ta.load_text('https://www.tinderpressroom.com/2023-02-27-TINDER-REDEFINES-EXPECTATIONS-WITH-NEW-BRAND-CAMPAIGN-THAT-CELEBRATES-GEN-ZS-AUTHENTIC,-FLUID-AND-BEAUTIFUL-CONNECTIONS', 'Tinder Advertising', parser=ta.custom_parser)


    # Dating App Reviews/Articles/Blogs
    # Hinge Review Article
    ta.load_text('https://tawkify.com/blog/dating-methods/hinge-dating-app-reviews', 'Hinge User Reviews', parser=ta.custom_parser)

    # Tinder Review Article
    ta.load_text('https://www.vanityfair.com/culture/2015/08/tinder-hook-up-culture-end-of-dating?srsltid=AfmBOopZi5hfIpFBEA7rG0cbGl-X4XwA4JYBL_RYEQLCFudbdF-I9gz3', 'Tinder User Reviews', parser=ta.custom_parser)

    # Plots
    ta.wordcount_sankey()
    ta.most_common_words()
    ta.plot_sentiment()
    ta.stacked_bar()
if __name__ == '__main__':
    main()