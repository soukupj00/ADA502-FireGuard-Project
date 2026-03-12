import { MapView } from "@/components/map/map-view"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ThemeProvider } from "@/components/theme-provider"
import { ModeToggle } from "@/components/mode-toggle"

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
        <header className="border-b bg-card">
          <div className="container mx-auto py-4 px-4 flex items-center justify-between">
             <div className="flex items-center gap-2">
               <div className="h-8 w-8 bg-primary rounded-md flex items-center justify-center text-primary-foreground font-bold text-xs shadow-sm">FG</div>
               <h1 className="text-xl font-bold tracking-tight">FireGuard</h1>
             </div>
             <ModeToggle />
          </div>
        </header>
        <main className="container mx-auto p-4 py-8 flex-1">
          <Card className="shadow-lg border-muted/40 overflow-hidden">
              <CardHeader className="bg-muted/10 border-b pb-6">
                  <CardTitle className="text-2xl">Fire Probability Map</CardTitle>
                  <CardDescription className="text-base text-muted-foreground">
                    Visualize fire risk across different regions based on real-time environmental data analysis.
                  </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                  <div className="h-150 w-full rounded-md overflow-hidden border shadow-inner relative z-0">
                      <MapView />
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 text-sm justify-center p-4 bg-muted/20 rounded-lg border">
                      <div className="flex items-center gap-2 justify-center">
                          <div className="w-4 h-4 bg-red-500 rounded ring-1 ring-red-600/20 shadow-sm"></div>
                          <span className="font-medium text-red-700 dark:text-red-400">High Risk (&gt; 80%)</span>
                      </div>
                      <div className="flex items-center gap-2 justify-center">
                          <div className="w-4 h-4 bg-orange-500 rounded ring-1 ring-orange-600/20 shadow-sm"></div>
                          <span className="font-medium text-orange-700 dark:text-orange-400">Medium-High (&gt; 50%)</span>
                      </div>
                      <div className="flex items-center gap-2 justify-center">
                          <div className="w-4 h-4 bg-yellow-500 rounded ring-1 ring-yellow-600/20 shadow-sm"></div>
                          <span className="font-medium text-yellow-700 dark:text-yellow-400">Medium-Low (&gt; 20%)</span>
                      </div>
                      <div className="flex items-center gap-2 justify-center">
                          <div className="w-4 h-4 bg-green-500 rounded ring-1 ring-green-600/20 shadow-sm"></div>
                          <span className="font-medium text-green-700 dark:text-green-400">Low Risk (&lt; 20%)</span>
                      </div>
                  </div>
              </CardContent>
          </Card>
        </main>
        <footer className="border-t py-6 text-center text-sm text-muted-foreground bg-muted/5">
          <div className="container mx-auto">
            &copy; {new Date().getFullYear()} FireGuard Project. All rights reserved.
          </div>
        </footer>
      </div>
    </ThemeProvider>
  )
}

export default App
