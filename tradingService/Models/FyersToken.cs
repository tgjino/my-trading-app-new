

namespace tradingService.Models;
public class FyersToken
{
    public int Id { get; set; }
    public string AccessToken { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public bool IsExpired => CreatedAt.AddDays(1) < DateTime.UtcNow; // Assuming token expires in 24 hours
}