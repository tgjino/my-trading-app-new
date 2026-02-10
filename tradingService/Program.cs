using Microsoft.AspNetCore.Http;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using tradingService.Data;
using tradingService.Models;


var builder = WebApplication.CreateBuilder(args);
builder.AddServiceDefaults();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddHttpClient("AnalyticsClient", client =>
{
    client.BaseAddress = new("http://python-backend");
});

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite("Data Source=trading.db"));
    
var app = builder.Build();

// അസ്പയർ ഡാഷ്‌ബോർഡിൽ ഹെൽത്ത് ചെക്കുകൾ കാണാൻ
app.MapDefaultEndpoints();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// --- പുതിയ ലോജിക് ഇവിടെ തുടങ്ങുന്നു ---
app.MapGet("/check-session", async (AppDbContext db, IHttpClientFactory clientFactory) =>
{
    var tokenEntry = await db.FyersTokens.OrderByDescending(t=> t.CreatedAt).FirstOrDefaultAsync();
    if (tokenEntry == null)
    {
        return Results.Ok(new { status = "NoToken", action = "/login"});
    }

    var client = clientFactory.CreateClient();
    client.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", tokenEntry.AccessToken);
    
    var response = await client.GetAsync("https://api-ti.fyers.in/api/v3/profile");
    if (response.IsSuccessStatusCode)
    {
        return Results.Ok(new { status = "Valid", token = tokenEntry.AccessToken });
    }
    else
    {
        return Results.Ok(new { status = "Expired", action = "/login"});
    }


});
app.MapGet("/login", (IConfiguration config) =>
{
    var clientId = config["Fyers:ClientId"];
    var redirect_uri = config["Fyers:RedirectUri"];
    var authUrl = $"https://api-t1.fyers.in/api/v3/generate-authcode?client_id={clientId}&driver_id=web&scope=all&state=sample_state&redirect_uri={redirect_uri}&response_type=code";
    return Results.Redirect(authUrl);
});

app.MapGet("/callback", async (string auth_code, IHttpClientFactory clientFactory, IConfiguration config, AppDbContext db) =>
{
    var clientId = config["Fyers:ClientId"];
    var secretKey = config ["Fyers:SecretKey"];
    
    string appIdHash;
    using (SHA256 sha256 = SHA256.Create())
    {
        string rawData = $"{clientId}:{secretKey}";
        byte[] bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(rawData));
        appIdHash = BitConverter.ToString(bytes).Replace("-", "").ToLower();
    }

    var client = clientFactory.CreateClient();

    var requestBody = new
    {
        grant_type = "authorization_code",
        appIdHash = appIdHash,
        code = auth_code
    };

    var response = await client.PostAsJsonAsync("https://api-t1.fyers.in/api/v3/validate-authcode", requestBody);
    
    if (response.IsSuccessStatusCode)
    {
        var responseData = await response.Content.ReadFromJsonAsync<System.Text.Json.JsonElement>();
        
        if (responseData.TryGetProperty("access_token", out var tokenProp))
        {
            var accessToken = tokenProp.GetString();
            var oldTokens = db.FyersTokens.ToList();
            db.FyersTokens.RemoveRange(oldTokens);

            var newToken = new tradingService.Models.FyersToken
            {
                AccessToken = accessToken ?? "",
                CreatedAt = DateTime.UtcNow
            };
            db.FyersTokens.Add(newToken);
            await db.SaveChangesAsync();
            // return Results.Ok(new { AccessToken = accessToken });
            try
            {
                var analyticsClient = clientFactory.CreateClient("AnalyticsClient");
                await analyticsClient.PostAsJsonAsync("/sync-to-python", new { access_token = accessToken });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error syncing to Python: {ex.Message}");
            }
            return Results.Redirect("/"); // Redirect to home or dashboard after successful login
        }
        else
        {
            return Results.Problem("Access token not found in response.");
        }
    }
    else
    {
        return Results.Problem("Failed to validate auth code.");
    }
});

app.MapGet("/test-python", async (IHttpClientFactory clientFactory) => {
    
    try
    {
        var client = clientFactory.CreateClient("AnalyticsClient");
        var response = await client.GetStringAsync("/test");
        return Results.Ok(new { Status = "Connected", PythonResponse = response});
    }
    catch (Exception ex)
    {
        return Results.Problem($"Could not connect to Python: {ex.Message}");
    }
});

app.MapPost("/sync-to-python", async (AppDbContext db, IHttpClientFactory clientFactory) => {
    Console.WriteLine("------Attempting to sync token to Python backend-----");

    var tokenEntry = await db.FyersTokens.OrderByDescending(t=> t.CreatedAt).FirstOrDefaultAsync();
    if (tokenEntry == null)
    {
        return Results.BadRequest("No valid token found in DB");
    }

    var client = clientFactory.CreateClient("AnalyticsClient");
    try {

        var response = await client.PostAsJsonAsync("/process-data", new { access_token = tokenEntry.AccessToken });
        var result = await response.Content.ReadAsStringAsync();
        Console.WriteLine($">>>> Python Response: {result}");
        return Results.Ok(result);
    }
    catch (Exception ex) {
        return Results.Problem(ex.Message);
    }
});


app.Run();

