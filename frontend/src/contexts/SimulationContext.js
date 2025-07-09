import React from 'react';

export const SimulationContext = React.createContext({
  clusterState: null,
  simulationState: null,
  API_URL: null
});

export const SimulationProvider = SimulationContext.Provider;
export const useSimulation = () => React.useContext(SimulationContext);