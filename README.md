# To install dependency
```
pip install python-dotenv discord.py chess cairosvg

```
# API Key
You need a free plan openweathermap api key and a discord bot api key to run the bot
# How to run
### Ubuntu
For installing stockfish
```
sudo apt install stockfish
```
Then you can run the bot by
```
chmod +x run.sh
./run.sh
```

### Windows
You need to download stockfish https://stockfishchess.org/download/
Then set the executable path of stockfish in run.bat like this for example
```
@SET STOCKFISH=C:\Users\user\Downloads\stockfish\stockfish-windows-x86-64-avx2 && python src\main.py
```
Then you can run it by
```
run.bat
```
# Initialize
You need to init your docs by using /init in the bot.
