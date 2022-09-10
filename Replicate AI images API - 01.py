# trzeba ustawić w systemie zmienną środowiskową z tokenem mojego konta w Replicate.com
# export REPLICATE_API_TOKEN=1dbd95063a1e0c766fee827b508cf18394c0fdbc
import replicate

model_AI = "stability-ai/stable-diffusion"
fraza = "beautiful spring garden with pond and fountain"
szer = 768
wys = 512

# teraz możemy dodać do słownika np. 3 różne modele AI
# i napisać pętlę generującą obrazy dla każdego z tych modeli
model = replicate.models.get(model_AI)
output = model.predict(prompt=fraza, width=szer, height=wys)


