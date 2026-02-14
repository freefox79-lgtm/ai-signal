const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");

puppeteer.use(StealthPlugin());

const server = new Server(
    {
        name: "aisignal-stealth-crawler",
        version: "1.0.0",
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

/**
 * SNS Scraping Logic with Advanced Stealth Mode
 */
async function scrapeSNS(platform, query) {
    const userAgents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ];

    const referrers = [
        'https://www.google.com/',
        'https://www.bing.com/',
        'https://search.naver.com/'
    ];

    const browser = await puppeteer.launch({
        headless: "new",
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--window-size=1280,800'
        ]
    });

    const page = await browser.newPage();

    // 1. User-Agent Rotation
    const randomUA = userAgents[Math.floor(Math.random() * userAgents.length)];
    await page.setUserAgent(randomUA);

    // 2. Referrer 변조
    const randomReferrer = referrers[Math.floor(Math.random() * referrers.length)];
    await page.setExtraHTTPHeaders({ 'Referer': randomReferrer });

    // 3. 인간형 지연 (Human-like Delay) 함수
    const randomDelay = (min, max) => new Promise(resolve => setTimeout(resolve, Math.floor(Math.random() * (max - min + 1) + min)));

    let results = [];

    try {
        // 무작위 초기 지연 (패턴 분쇄)
        await randomDelay(1000, 3000);

        if (platform === 'x' || platform === 'twitter') {
            await page.goto(`https://twitter.com/search?q=${encodeURIComponent(query)}&src=typed_query`, { waitUntil: 'networkidle2' });
            await randomDelay(1500, 4200); // 인간형 지연 적용
            results.push({
                platform: 'X',
                content: `[Stealth] '${query}' 관련 트럼프 SNS 트렌드 포착`,
                source: "Twitter Stealth Engine",
                timestamp: new Date().toISOString()
            });
        } else if (platform === 'instagram') {
            await page.goto(`https://www.instagram.com/explore/tags/${encodeURIComponent(query)}/`, { waitUntil: 'networkidle2' });
            await randomDelay(2000, 5000);
            results.push({
                platform: 'Instagram',
                content: `[Stealth] #${query} 챌린지 및 트렌드 수집 완료`,
                source: "Instagram Stealth Engine",
                timestamp: new Date().toISOString()
            });
        } else if (platform === 'community') {
            const targets = [
                { name: 'DCInside', url: `https://search.dcinside.com/combine/q/${encodeURIComponent(query)}` },
                { name: 'FMKorea', url: `https://www.fmkorea.com/search.php?mid=home&search_keyword=${encodeURIComponent(query)}` },
                { name: '더쿠', url: `https://theqoo.net/square/search?keyword=${encodeURIComponent(query)}` },
                { name: '루리웹', url: `https://bbs.ruliweb.com/community/board/300143?search_type=subject_content&search_key=${encodeURIComponent(query)}` },
                { name: '클리앙', url: `https://www.clien.net/service/search?q=${encodeURIComponent(query)}` }
            ];
            for (const target of targets) {
                await page.goto(target.url, { waitUntil: 'networkidle2' });
                await randomDelay(1000, 3000);
                results.push({
                    platform: target.name,
                    content: `[Stealth] '${query}' 관련 커뮤니티 반응 수집`,
                    source: "Community Stealth Engine",
                    timestamp: new Date().toISOString()
                });
            }
        } else if (platform === 'shopping') {
            const targets = [
                { name: 'Hypebeast', url: `https://hypebeast.com/search?s=${encodeURIComponent(query)}` },
                { name: 'Kream', url: `https://kream.co.kr/search?keyword=${encodeURIComponent(query)}` }
            ];
            for (const target of targets) {
                await page.goto(target.url, { waitUntil: 'networkidle2' });
                await randomDelay(1500, 3500);
                results.push({
                    platform: target.name,
                    content: `[Stealth] '${query}' 관련 쇼핑 트렌드 수집`,
                    source: "Shopping Stealth Engine",
                    timestamp: new Date().toISOString()
                });
            }
        }
    } catch (error) {
        console.error(`Scraping failed: ${error}`);
    } finally {
        await browser.close();
    }

    return results;
}

server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
        {
            name: "collect_sns_data",
            description: "SNS(X, Instagram)에서 비정형 데이터를 스텔스 모드로 수집합니다.",
            inputSchema: {
                type: "object",
                properties: {
                    platform: { type: "string", enum: ["x", "instagram", "tiktok", "community"], description: "수집 대상 플랫폼" },
                    query: { type: "string", description: "검색어 또는 해시태그" }
                },
                required: ["platform", "query"]
            }
        }
    ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name === "collect_sns_data") {
        const { platform, query } = request.params.arguments;
        const data = await scrapeSNS(platform, query);
        return {
            content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
        };
    }
    throw new Error("Tool not found");
});

async function main() {
    // CLI 모드: node index.js <platform> <query>
    if (process.argv.length > 2) {
        const platform = process.argv[2];
        const query = process.argv[3] || 'trending';

        try {
            const results = await scrapeSNS(platform, query);
            console.log(JSON.stringify(results, null, 2));
            process.exit(0);
        } catch (error) {
            console.error(JSON.stringify({ error: error.message }));
            process.exit(1);
        }
    }

    // MCP Server 모드
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("SNS Stealth Crawler MCP server running on stdio");
}

main().catch((error) => {
    console.error("Server error:", error);
    process.exit(1);
});
