using System.Reflection;
using Aspire.Hosting;
var builder = DistributedApplication.CreateBuilder(args);

var clientId = builder.Configuration["Fyers:ClientId"];
var secretKey = builder.Configuration["Fyers:SecretKey"];
var redirectUri = builder.Configuration["Fyers:RedirectUri"];
                    
var pythonBackend = builder.AddPythonApp("python-backend", "../ai-analytics", "api_app.py")
                    .WithEnvironment("client_id", clientId)
                    .WithEnvironment("secret_key", secretKey)
                    .WithEnvironment("redirect_uri", redirectUri)
                    .WithEnvironment("DB_PATH", "tradingData.db")
                    .WithHttpEndpoint(targetPort: 8000,name:"http", env: "PORT")
                    .WithExternalHttpEndpoints();

var tradesEngine = builder.AddPythonApp( name: "tradesEngine", 
                                        projectDirectory: "../tradesEngineMain", 
                                        scriptPath: "tradesEngine.py", 
                                        virtualEnvironmentPath: "../tradesEngineMain/.venv" )
                                        .WithHttpEndpoint(targetPort: 4000)
                                        .WithExternalHttpEndpoints();

var tradingService = builder.AddProject<Projects.tradingService>("tradingService")
                                        .WithEnvironment("Fyers__ClientId", clientId)
                                        .WithEnvironment("Fyers__SecretKey", secretKey)
                                        .WithEnvironment("Fyers__RedirectUri", redirectUri)
                                        .WithReference(tradesEngine)                
                                        .WithReference(pythonBackend);

builder.AddNpmApp("frontend", "../my-trading-app-face", "dev")
    .WithReference(tradingService)
    .WithReference(pythonBackend)
    .WithHttpEndpoint(env: "PORT", port: 3000)
    .WithExternalHttpEndpoints();

builder.Build().Run();