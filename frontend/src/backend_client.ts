// backendRequests.ts
export class BackendClient {
  private static instance: BackendClient | null = null;
  private baseUrl: string;

  private constructor(baseUrl: string = "https://bistered-gaylord-contorted.ngrok-free.dev") {
    this.baseUrl = baseUrl;
  }

  static getInstance(): BackendClient {
    if (!BackendClient.instance) {
      BackendClient.instance = new BackendClient();
    }
    return BackendClient.instance;
  }

  // Optional: Method to explicitly set base URL after instantiation
  setBaseUrl(baseUrl: string): void {
    this.baseUrl = baseUrl;
  }

  // Optional: Get current base URL
  getBaseUrl(): string {
    return this.baseUrl;
  }

  private fetchJson<T>(appendix: string, init?: RequestInit): Promise<T> {
    // Always include the ngrok header
    const headers = {
      "ngrok-skip-browser-warning": "69420",
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    };

    return fetch(this.baseUrl + appendix, { ...init, headers })
      .then(async res => {
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }

        const contentType = res.headers.get("content-type");

        if (!contentType || !contentType.includes("application/json")) {
          throw new Error("Response is not JSON");
        }

        return res.json() as Promise<T>;
      })
      .catch(err => {
        console.error("Error connecting to backend:", err);
        throw err;
      });
  }

  loadModel(model: string) {
    return this.fetchJson("/model/load?model=" + model, {
      method: "POST"
    });
  }

  resetModel(model: string) {
    return this.fetchJson("/model/reset", {
      method: "POST",
      body: JSON.stringify({ model }),
    });
  }

  getModelArchitecture(model: string) {
    return this.fetchJson(`/model/architecture?model=${encodeURIComponent(model)}`)
      .then(res => res.architecture);
  }

  getLayerNames(model: string) {
    return this.fetchJson(`/model/layers?model=${encodeURIComponent(model)}`)
      .then(res => res.layers);
  }

  generateOutput(model: string, prompt: string) {
    return this.fetchJson(`/model/generate?model=${encodeURIComponent(model)}&prompt=${encodeURIComponent(prompt)}`)
      .then(res => res.generated);
  }

  getLayerActivations(model: string, layerName: string) {
    return this.fetchJson(`/model/layer/${encodeURIComponent(layerName)}/activations?model=${encodeURIComponent(model)}`)
      .then(res => res.activations);
  }

  getLayerBiases(model: string, layerName: string) {
    return this.fetchJson(`/model/layer/${encodeURIComponent(layerName)}/biases?model=${encodeURIComponent(model)}`);
  }

  getLayerInputAvgs(model: string, layerName: string) {
    return this.fetchJson(`/model/layer/${encodeURIComponent(layerName)}/input-avgs?model=${encodeURIComponent(model)}`)
      .then(res => res.input_avgs);
  }

  getLayerInputStds(model: string, layerName: string) {
    return this.fetchJson(`/model/layer/${encodeURIComponent(layerName)}/input-stds?model=${encodeURIComponent(model)}`)
      .then(res => res.input_stds);
  }

  setNeuronBias(model: string, layerName: string, neuronIndex: number, biasValue: number) {
    return this.fetchJson(`/model/layer/${encodeURIComponent(layerName)}/bias/${neuronIndex}/set`, {
      method: "POST",
      body: JSON.stringify({ model, bias_value: biasValue }),
    });
  }

  setTimestep(model: string, index: number) {
    return this.fetchJson("/model/timestep/set", {
      method: "POST",
      body: JSON.stringify({ model, index }),
    });
  }
}

// Usage examples:
// const client = BackendClient.getInstance();
// client.setBaseUrl("https://custom-url.com");
// 
// Anywhere else in your app:
// const client = BackendClient.getInstance(); // Same instance, no need to specify URL again