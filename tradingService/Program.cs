using Microsoft.AspNetCore.Http;
using System.Net.Http;
// using MyTradingApp.ServiceDefaults;

var builder = WebApplication.CreateBuilder(args);
builder.AddServiceDefaults();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddHttpClient("AnalyticsClient", client =>
{
    client.BaseAddress = new("http://python-backend");
});

var app = builder.Build();

// അസ്പയർ ഡാഷ്‌ബോർഡിൽ ഹെൽത്ത് ചെക്കുകൾ കാണാൻ
app.MapDefaultEndpoints();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

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

app.MapPost("/send-to-python", async (string token, IHttpClientFactory clientFactory) => {
    var client = clientFactory.CreateClient("AnalyticsClient");
    try {
        var response = await client.PostAsJsonAsync("/process-data", new { access_token = token });
        var result = await response.Content.ReadAsStringAsync();
        return Results.Ok(result);
    }
    catch (Exception ex) {
        return Results.Problem(ex.Message);
    }
});

app.MapGet("/",() => "Trading Service is Running ");


app.Run();

