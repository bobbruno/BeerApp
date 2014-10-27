'''
Created on 19/10/2014

@author: bobbruno
'''

import floppyforms as forms


#  Slider = None

class Slider(forms.RangeInput):
    min = -5
    max = 5
    step = 0.5
    #  template_name = 'slider.html'

    class Media:
        js = (
            'js/jquery.min.js',
            'js/jquery-ui.min.js',
        )
        css = {
            'all': (
                'css/jquery-ui.css',
            )
        }


class SliderField(forms.FloatField):
    def __init__(self, rlabel, *args, **kwargs):
        super(forms.FloatField, self).__init__(*args, **kwargs)
        self.rlabel = rlabel

    def rlabel(self):
        return self.rlabel


class PollForm(forms.Form):
    q1 = SliderField(label='Thick head, dark brown/black. Aroma is roasted malts, spices, caramel, fruit, chocolate. Full rich body, alcohol taste. Creamy, dry finish',
                     rlabel="Medium head. Clear, pale golden/straw color. Hoppy, grassy aroma. Refreshing acid/bitter taste. Thin body. Bittersweet finish",
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q2 = SliderField(label="Medium white head. Cloudy amber/gold color. Grapefruit, floral, hoppy aroma, refreshing, caramel taste, strong body, creamy mouthfeel, dry finish",
                     rlabel='Beige small  head. Clear, dark brown color. Fruity, roasted malts, strong coffee, chocolate aroma. Sweet, sour taste, medium body',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q3 = SliderField(label="Hazy light straw/yellow color, medium head. Spices, yeast and wheat aroma, banana and cloves. Little carbonation. Sweet taste",
                     rlabel='Clear amber/golden color, small white head. Grass, strong hops aroma, orange notes. Bitter taste, dry finish',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q4 = SliderField(label="Clear reddish brown. Warming alcohol, complex fruity sweet aroma, very malty, notes of wood, full body, dry finish",
                     rlabel='Clear pale golden, strong carbonation, Light sweet grains and caramel aroma, bitter thin taste, light body. Crisp aftertaste',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q5 = SliderField(label="Only in bottles. Clear yellow, soft carbonation, lasting head. Aroma of malt, hops and herbs. Bitter taste, bittersweet finish",
                     rlabel='Striking bottle design. Dark, transparent yellow. Aroma of stale hops, corn and strong alcohol. Dry, watery, oily taste, with strong alcohol accents',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q6 = SliderField(label="Clear Reddish amber/brown color, small off-white head and lacing. Toffee, caramel malt aroma. Sweet malt taste, medium body. Sweet aftertaste",
                     rlabel='Hazy straw/golden color, thick lasting white head, with strong lacing. Citrus, tropical fruits and strong hops aroma. Bitter/citrusy hops taste and bitter, dry  aftertaste',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q7 = SliderField(label="Hazy yellow. Aroma of banana, cloves and citrus. Flavor follows. Acid, bittersweet finish, some yeast",
                     rlabel='Dark reddish, murky brown, some bubbles. Aroma of cherries, wine, wood and vinegar. Sour malty taste. Tart, sour finish',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q8 = SliderField(label="Pitch black, little brown head. High alcohol content. Alcohol aroma, with peat and chocolate. Taste follows aroma with some sweetness. Full body. Alcohol, peat, dry finish",
                     rlabel='From cask. Clear reddish brown color, off-white head. Malt and citrus aromas, taste of malt, toffee and caramel. Medium body. Bitter and sweet finish',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q9 = SliderField(label="Orange/brown color. Aroma of red fruits and cherries. Sour, acid taste, with hints of caramel. Tart, fruity finish",
                     rlabel='Cloudy golden. Aroma of citrus, wheat, caramel and spices, with hops. Mildly bitter taste with lots of malt and dry aftertaste',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q10 = SliderField(label="Clear copper/amber. Smell of sugar, apples and alcohol. Alcohol and sugar candy taste",
                      rlabel='Hazy orange/amber color. Smell of lemon, hops and acetone, sour and yeast notes. Medium carbonation, light body. Bitter flavor, together with sourness in aftertaste',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
