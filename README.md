# Portafolio de Boston · Editor de video

Sitio estático publicado con GitHub Pages en https://bostonmalbec-tech.github.io

- `plantilla.html`: diseño, estilos y animaciones de la página.
- `videos.json`: lista de videos (título, canal, enlace, formato).
- `build.py`: arma `index.html` a partir de la plantilla y la lista.

Para agregar videos de YouTube (lee el título y el canal solo):

```bash
python3 build.py add ID_DEL_VIDEO OTRO_ID
```

Para reconstruir la página después de editar la plantilla o la lista:

```bash
python3 build.py
```
