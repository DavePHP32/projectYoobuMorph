npm run build

zip -r deploy.zip dist prisma package.json package-lock.json

unzip -o deploy.zip -d .deployment

cd .deployment

npm install

zip -r deploy.zip .

az webapp deploy \
  --resource-group rg-latel-dev \
  --name yoobu-morph \
  --src-path deploy.zip \
  --type zip

