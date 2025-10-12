# Stage 2: TinyLlama via Ollama on Azure VM
## 1. Provision the VM
REGION="eastus"
COMPUTING_ID="<your-computing-id>"
RG_VM="uva-sds-gpt-pzd5fp-vm-rg"
VM_NAME="ollama-tinyllama-pzd5fp"

az group create --name "UVA-SDS-GPT-PZD5FP-VM-RG3" --location "westus3"
az vm create 
  --resource-group "UVA-SDS-GPT-PZD5FP-VM-RG3" --name "ollama-tinyllama-pzd5fp" 
  --image "Ubuntu2204" --admin-username "azureuser" 
  --generate-ssh-keys --public-ip-sku Standard 
  --size Standard_B2s

# Open port 11434 for Ollama
az vm open-port --resource-group "UVA-SDS-GPT-PZD5FP-VM-RG3" --name "ollama-tinyllama-pzd5fp" --port 11434 --priority 1001

## 2. SSH into VM & install Ollama
# ssh azureuser@4.154.186.49
curl -fsSL https://ollama.com/install.sh | sh

# Bind Ollama to all interfaces
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now ollama
systemctl status ollama

# Pull TinyLlama model
ollama pull tinyllama

# Test locally
curl -s http://127.0.0.1:11434/api/generate -d '{"model":"tinyllama","prompt":"Say hi"}'

## 3. Connect App Service to VM
APP_NAME="uva-sds-gpt-pzd5fp"
RG_APP="uva-sds-gpt-pzd5fp-rg"

az webapp config appsettings set 
  --name "uva-sds-gpt-pzd5fp" --resource-group "uva-sds-gpt--rg" 
  --settings OLLAMA_URL="http://" OLLAMA_MODEL="tinyllama"

az webapp restart -g "uva-sds-gpt--rg" -n "uva-sds-gpt-pzd5fp"

## 4. Verify
# Health
curl -s https://uva-sds-gpt-pzd5fp.azurewebsites.net/api/health

# Chat
curl -s -X POST https://uva-sds-gpt-pzd5fp.azurewebsites.net/api/chat 
  -H "Content-Type: application/json" 
  -d '{"text":"One fun UVA fact in one sentence."}'
