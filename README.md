# Portafolio de Boston · Editor de video

Sitio estático publicado con GitHub Pages en https://bostonmalbec-tech.github.io

- `videos.json`: lista de videos (título, canal, enlace, formato, etiquetas).
- `build.py`: genera `index.html`, una sola página larga con portada, sobre mí, creadores y una sección por creador.
- `assets/styles.css` y `assets/app.js`: diseño y animaciones compartidas.
- `img/oso.png`: la mascota.

Para agregar videos de YouTube (lee el título y el canal solo):

```bash
python3 build.py add ID_DEL_VIDEO OTRO_ID
```

Para reconstruir la página después de editar la lista o el generador:

```bash
python3 build.py
```
