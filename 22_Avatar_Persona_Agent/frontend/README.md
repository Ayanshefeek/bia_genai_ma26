# Frontend scaffold

This is the browser side of the Avatar Persona Agent practical.

Run it from the `frontend/` folder:

```bash
npm install
npm run dev
```

Open the URL printed by Vite, usually `http://127.0.0.1:5173`.

The avatar is intentionally procedural. It avoids external 3D asset downloads so the classroom demo works even when GLB asset loading fails. The extension path is to replace `ProceduralAvatar.jsx` with a GLB-based avatar using morph targets.
