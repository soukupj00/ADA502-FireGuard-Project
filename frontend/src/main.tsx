import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import App from "./App.tsx"
import keycloak from "./keycloak"
import { ThemeProvider } from "@/components/theme-provider.tsx"
import { Toaster } from "@/components/ui/sonner"

keycloak
  .init({
    onLoad: "check-sso",
    silentCheckSsoRedirectUri:
      window.location.origin + "/silent-check-sso.html",
    // Stops the browser from blocking the NREC IP hidden iframe
    checkLoginIframe: false,
  })
  .then((authenticated: boolean) => {
    const rootElement = document.getElementById("root")
    if (!rootElement) throw new Error("Root element not found")

    createRoot(rootElement).render(
      <StrictMode>
        <ThemeProvider>
          <App isAuthenticated={authenticated} />
          <Toaster />
        </ThemeProvider>
      </StrictMode>
    )
  })
  .catch((error: unknown) => {
    console.error("Keycloak initialization failed", error)
  })
