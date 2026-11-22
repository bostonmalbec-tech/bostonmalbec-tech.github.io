# Portafolio de Boston · Editor de video

Sitio estático publicado con GitHub Pages en https://bostonmalbec-tech.github.io

- `videos.json`: lista de videos (título, canal, enlace, formato, etiquetas).
- `build.py`: genera todas las páginas (`index.html`, `sobre-mi.html`, `trabajos.html`, `contacto.html` y una página por creador en `trabajos/`).
- `assets/styles.css` y `assets/app.js`: diseño y animaciones compartidas.
- `img/oso.png`: la mascota.

Para agregar videos de YouTube (lee el título y el canal solo):

```bash
python3 build.py add ID_DEL_VIDEO OTRO_ID
```

Para reconstruir las páginas después de editar la lista o el generador:

```bash
python3 build.py
```
