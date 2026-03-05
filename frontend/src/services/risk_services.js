import { useEffect, useState } from "react";

function TestRiskAPI() {
  const [risk, setRisk] = useState(null);

  useEffect(() => {
    async function fetchRisk() {
      try {
        const response = await fetch(
          "http://localhost:8000/api/v1/risk/coords?latitude=59.91&longitude=10.75"
        );
        if (!response.ok) throw new Error("API request failed");
        const data = await response.json();
        setRisk(data);
      } catch (err) {
        console.error(err);
      }
    }

    fetchRisk();
  }, []);

  return <div>{risk ? `Fire Risk Level: ${risk.risk_level}` : "Loading..."}</div>;
}

export default TestRiskAPI;