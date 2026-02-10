using Microsoft.EntityFrameworkCore;
using tradingService.Models;


namespace tradingService.Data;
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
        
    }

    public DbSet<FyersToken> FyersTokens { get; set; }
}