from googletrans import Translator

transltor = Translator(service_urls=['translate.google.com'])
translations = transltor.translate(
    ['leather-and-synthetic', 'Real and synthetic leather upper for an elevated look and feel',
     'TPU cage extends from heel to forefoot for increased support'], dest='ru')
for translation in translations:
    print(translation.origin, '->', translation.text)
