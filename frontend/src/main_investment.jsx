import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { HeroUIProvider } from "@heroui/react";
import "./index.css";


createRoot(document.getElementById("root")).render(
  <StrictMode>
    <HeroUIProvider>
      <main className="dark text-foreground bg-background">
        <Investment />
      </main>
    </HeroUIProvider>
  </StrictMode>
);
