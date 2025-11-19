// backend_client.ts
export class BackendClient {
  private static instance: BackendClient | null = null;
  private baseUrl: string;

  constructor(baseUrl: string = "https://bistered-gaylord-contorted.ngrok-free.dev") {
    this.baseUrl = baseUrl;
  }

  static getInstance(baseUrl?: string): BackendClient {
    if (!BackendClient.instance) {
      BackendClient.instance = new BackendClient(baseUrl);
    }
    return BackendClient.instance;
  }

  setBaseUrl(baseUrl: string): void {
    this.baseUrl = baseUrl;
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }

  private async fetchJson<T>(appendix: string, init?: RequestInit): Promise<T> {
    const headers = {
      "ngrok-skip-browser-warning": "69420",
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    };

    try {
      const res = await fetch(this.baseUrl + appendix, { ...init, headers });
      
      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }

      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("Response is not JSON");
      }

      return res.json() as Promise<T>;
    } catch (err) {
      console.error("Error connecting to backend:", err);
      throw err;
    }
  }

  // POST /model/load
  loadModel(model: string) {
    return this.fetchJson<{ status: string; model: string }>(
      `/model/load?model=${encodeURIComponent(model)}`,
      { method: "POST" }
    );
  }

  // POST /model/reset
  resetModel(model: string) {
    return this.fetchJson<{ status: string; model: string }>(
      `/model/reset?model=${encodeURIComponent(model)}`,
      { method: "POST" }
    );
  }

  // GET /model/architecture
  async getModelArchitecture(model: string) {
    const res = await this.fetchJson<{ architecture: any }>(
      `/model/architecture?model=${encodeURIComponent(model)}`
    );
    return res.architecture;
  }

  // GET /model/layers
  async getLayerNames(model: string) {
    const res = await this.fetchJson<{ layers: string[] }>(
      `/model/layers?model=${encodeURIComponent(model)}`
    );
    return res.layers;
  }

  // GET /model/generate
  async generateOutput(model: string, prompt: string) {
    const res = await this.fetchJson<{ generated: string }>(
      `/model/generate?model=${encodeURIComponent(model)}&prompt=${encodeURIComponent(prompt)}`
    );
    return res.generated;
  }

  // GET /model/activations
  async getLayerActivations(model: string, layerName: string) {
    const res = await this.fetchJson<{ activations: any }>(
      `/model/activations?model=${encodeURIComponent(model)}&layer_name=${encodeURIComponent(layerName)}`
    );
    return res.activations;
  }

  // GET /model/biases
  getLayerBiases(model: string, layerName: string) {
    console.log('fetching', `/model/biases?model=${encodeURIComponent(model)}&layer_name=${encodeURIComponent(layerName)}`)
    return this.fetchJson<any>(
      `/model/biases?model=${encodeURIComponent(model)}&layer_name=${encodeURIComponent(layerName)}`
    );
  }

  // GET /model/input-avgs
  async getLayerInputAvgs(model: string, layerName: string) {
    const res = await this.fetchJson<{ input_avgs: any }>(
      `/model/input-avgs?model=${encodeURIComponent(model)}&layer_name=${encodeURIComponent(layerName)}`
    );
    return res.input_avgs;
  }

  // GET /model/input-stds (Note: Python route is missing leading slash)
  async getLayerInputStds(model: string, layerName: string) {
    const res = await this.fetchJson<{ input_stds: any }>(
      `/modelinput-stds?model=${encodeURIComponent(model)}&layer_name=${encodeURIComponent(layerName)}`
    );
    return res.input_stds;
  }

  // POST /model/set-neuron-bias
  setNeuronBias(model: string, layerName: string, neuronIndex: number, biasValue: number) {
    return this.fetchJson<{ status: string }>(
      `/model/set-neuron-bias?model=${encodeURIComponent(model)}&layer_name=${encodeURIComponent(layerName)}&neuron_index=${neuronIndex}&bias_value=${biasValue}`,
      { method: "POST" }
    );
  }

  // POST /model/timestep
  setTimestep(model: string, index: number) {
    return this.fetchJson<{ timestep: number }>(
      `/model/timestep?model=${encodeURIComponent(model)}&index=${index}`,
      { method: "POST" }
    );
  }
}
