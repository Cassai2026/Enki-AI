# auth/registry/

Place authorized user face photos here.

Each file must be a `.jpg` or `.png` image containing a clear, front-facing photo of an authorized user.

**Naming convention:** `<username>.jpg` (e.g., `admin.jpg`, `naz.jpg`)

The `FaceAuthenticator` will compare the live camera feed against **every** image in this directory.
Authentication succeeds if the live face matches **any** registered user.

> **Security note:** Never commit real biometric images to version control.
> Add this directory to `.gitignore` if needed, or store only placeholder/test images.
