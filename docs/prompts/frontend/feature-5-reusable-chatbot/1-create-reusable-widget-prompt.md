Task: Create a reusable AI Chat Widget foundation inside frontend/lib/ai-widget.

Requirements:

Folder Structure:

lib/
└── ai-widget/
    ├── core/
    ├── components/
    ├── services/
    ├── adapters/
    ├── types/
    ├── styles/
    └── index.ts

Guidelines:

1. Keep all AI widget code isolated from Doctor Appointment features.

2. Widget should expose a clean public API.

3. Business-specific logic must reside in adapters.

4. Design the architecture so that the entire ai-widget folder can later be extracted into a standalone package.

5. Do not implement backend integration yet.

6. Do not implement AI logic yet.

7. Only create the foundation, public interfaces, types, and component skeletons.