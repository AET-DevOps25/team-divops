import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import { BrowserRouter } from "react-router";
import { createTheme, MantineProvider } from "@mantine/core";

const theme = createTheme({});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <MantineProvider
        forceColorScheme="dark"
        defaultColorScheme="dark"
        theme={theme}
      >
        <App />
      </MantineProvider>
    </BrowserRouter>
  </StrictMode>
);
