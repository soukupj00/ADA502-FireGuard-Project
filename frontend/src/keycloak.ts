import Keycloak from "keycloak-js"

const keycloakConfig = {
  // Use a relative path. Nginx/Vite will route this to the Keycloak container.
  url: "/auth",
  realm: "FireGuard",
  clientId: "react-app",
}

const keycloak = new Keycloak(keycloakConfig)

export default keycloak
