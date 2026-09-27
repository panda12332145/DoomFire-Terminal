# como contribuir

quer ajudar, manda bala

## estrutura

- config: configuracao, paletas, tamanho
- core: engine principal
- collection: logica de propagacao do fogo
- payloads: render
- execution: loop e cli

## rodar local

```bash
git clone https://github.com/panda12332145/DoomFire-Terminal.git
cd DoomFire-Terminal/DoomFire-Terminal
pip install -e .[dev]
python doomfire.py --interactive --stats
pytest tests/ -v
```

## padrao

- usa snake_case
- comenta na mesma linha, sem acento, virgula meio errada mesmo kkk
- mantem simples, sem frescura
- testa antes de mandar PR

## cli

```bash
python doomfire.py --width 80 --height 30 --palette blue --interactive
```
