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
    q1 = SliderField(label='Thick head, alcohol, dark brown or black, full rich body, strong taste, roasted malts, spices, caramel, fruit, chocolate aroma, creamy, dry finish',
                     rlabel="Medium head, refereshing, acid, Bitter, clear, pale golden/straw color, fresh, hoppy, malty, grassy, light flavor, thin texture, bitter finish",
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q2 = SliderField(label="Medium white head, lasting lacing, alcohol, cloudy amber/gold, malty, grapefruit, floral, very strong hoppy citrus, refreshing, caramel, strong body, creamy mouthfeel, dry finish",
                     rlabel='Beige small  head, clear, dark brown, fruity, roasted malts, strong coffee, chocolate aroma, sweet, sour, medium body',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q3 = SliderField(label="Hazy light straw/yellow color, medium head. Spices, yeast and wheat aroma, banana and cloves, lemon. Little carbonation. Sweet taste.",
                     rlabel='Clear amber/golden color, small white head. Grass, strong hops and citrus aroma, orange notes. Bitter taste, dry finish.',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q4 = SliderField(label="Clear reddish brown, small brown head. Warming alcohol, complex fruity sweet aroma, very malty, notes of wood, full body, dry finish.",
                     rlabel='Clear pale golden, strong carbonation, Light sweet grains and caramel aroma, bitter thin taste, light body. Crisp aftertaste',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q5 = SliderField(label="Question 5", rlabel='Test 5',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q6 = SliderField(label="Question 6", rlabel='Test 6',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q7 = SliderField(label="Question 7", rlabel='Test 7',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q8 = SliderField(label="Question 8", rlabel='Test 8',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q9 = SliderField(label="Question 9", rlabel='Test 9',
                     widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q10 = SliderField(label="Question 10", rlabel='Test 10',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q11 = SliderField(label="Question 11", rlabel='Test 11',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q12 = SliderField(label="Question 12", rlabel='Test 12',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q13 = SliderField(label="Question 13", rlabel='Test 13',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q14 = SliderField(label="Question 14", rlabel='Test 14',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q15 = SliderField(label="Question 15", rlabel='Test 15',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q16 = SliderField(label="Question 16", rlabel='Test 16',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q17 = SliderField(label="Question 17", rlabel='Test 17',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q18 = SliderField(label="Question 18", rlabel='Test 18',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q19 = SliderField(label="Question 19", rlabel='Test 19',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
    q20 = SliderField(label="Question 20", rlabel='Test 20',
                      widget=Slider({'min': 0., 'max': 1., 'step': 0.1}))
