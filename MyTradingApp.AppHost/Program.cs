using System.Reflection;
using Aspire.Hosting;
var builder = DistributedApplication.CreateBuilder(args);

var clientId = builder.Configuration["Fyers:ClientId"];
var secretKey = builder.Configuration["Fyers:SecretKey"];
var redirectUri = builder.Configuration["Fyers:RedirectUri"];

var netBackend = builder.AddProject<Projects.tradingService>("net-backend");
var pythonBackend = builder.AddPythonApp("python-backend", "../ai-analytics", "api_app.py")
                    .WithEnvironment("client_id", clientId)
                    .WithEnvironment("secret_key", secretKey)
                    .WithEnvironment("redirect_uri", redirectUri)
                    .WithEnvironment("DB_PATH", "tradingData.db")
                    .WithHttpEndpoint(targetPort: 8000)
                    .WithExternalHttpEndpoints()
                    .WithReference(netBackend);

builder.AddNpmApp("frontend", "../my-trading-app-face", "dev")
    .WithReference(netBackend)
    .WithReference(pythonBackend)
    .WithHttpEndpoint(env: "PORT", port: 3000)
    .WithExternalHttpEndpoints();

builder.Build().Run();