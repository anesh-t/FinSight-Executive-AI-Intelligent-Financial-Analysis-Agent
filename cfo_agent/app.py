"""
FastAPI service for CFO Agent
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache
from hitl import hitl_gate
from viz_data_fetcher import VizDataFetcher  # NEW: Visualization support


# Pydantic models
class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"
    enable_hitl: Optional[bool] = False


class QueryResponse(BaseModel):
    response: str
    session_id: str
    viz_metadata: Optional[Dict[str, Any]] = None  # NEW: Optional visualization metadata


# NEW: Visualization models (completely separate from existing)
class VisualizationRequest(BaseModel):
    session_id: str
    intent: str
    params: dict
    question: Optional[str] = None  # NEW: Original question for metric detection


class VisualizationResponse(BaseModel):
    chart_data: dict
    chart_config: dict


# FastAPI app
app = FastAPI(
    title="CFO Agent API",
    description="Structured-only CFO Analytics Agent with LangGraph + LangChain",
    version="1.0.0"
)

# NEW: Global visualization fetcher (initialized in startup)
viz_fetcher = None


@app.on_event("startup")
async def startup_event():
    """Initialize database connections and caches on startup"""
    print("🚀 Starting CFO Agent...")
    
    # Initialize database pool
    await db_pool.initialize()
    print("✅ Database pool initialized")
    
    # Load schema cache
    await load_schema_cache()
    print("✅ Schema cache loaded")
    
    # Load ticker cache
    await load_ticker_cache()
    print("✅ Ticker cache loaded")
    
    # NEW: Initialize visualization fetcher
    global viz_fetcher
    viz_fetcher = VizDataFetcher(db_pool.pool)
    print("✅ Visualization fetcher initialized")
    
    print("🎉 CFO Agent ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("👋 Shutting down CFO Agent...")
    await db_pool.close()
    print("✅ Database pool closed")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CFO Agent",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "schema_cache": "loaded",
        "ticker_cache": "loaded"
    }


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a question to the CFO Agent
    
    Args:
        request: QueryRequest with question and optional session_id
        
    Returns:
        QueryResponse with formatted answer and optional viz_metadata
    """
    try:
        # Enable/disable HITL based on request
        if request.enable_hitl:
            hitl_gate.enable()
        else:
            hitl_gate.disable()
        
        # Run the agent graph and get full state
        initial_state = {
            'question': request.question,
            'session_id': request.session_id,
            'errors': []
        }
        final_state = await cfo_agent_graph.graph.ainvoke(initial_state)
        
        # Extract response
        response_text = final_state.get('final_response', 'Error: No response generated')
        
        # NEW: Check if visualization is available
        viz_metadata = None
        if viz_fetcher:
            # Get first plan (contains intent and params)
            plans = final_state.get('plans', [])
            
            if plans and len(plans) > 0:
                plan = plans[0]
                intent = plan.get('intent', '')
                params = plan.get('params', {})
                
                print(f"[VIZ CHECK] Intent: {intent}, Params: {params}")
                print(f"[VIZ CHECK] Should visualize: {viz_fetcher.should_visualize(intent, params)}")
                
                # Check if viz is applicable
                if intent and params and viz_fetcher.should_visualize(intent, params):
                    viz_metadata = {
                        'available': True,
                        'intent': intent,
                        'params': params,
                        'chart_type': viz_fetcher.get_chart_type(intent, params),
                        'question': request.question  # NEW: Pass original question for metric detection
                    }
                    print(f"[VIZ CHECK] Metadata created: {viz_metadata}")
        
        return QueryResponse(
            response=response_text,
            session_id=request.session_id,
            viz_metadata=viz_metadata
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )


@app.get("/session/{session_id}/context")
async def get_session_context(session_id: str):
    """Get session context/memory"""
    from memory import session_memory
    
    context = session_memory.get_context_summary(session_id)
    session = session_memory.get_or_create_session(session_id)
    
    return {
        "session_id": session_id,
        "context_summary": context,
        "last_tickers": session['last_tickers'],
        "last_period": session['last_period'],
        "query_count": session['query_count']
    }


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session memory"""
    from memory import session_memory
    
    session_memory.clear_session(session_id)
    
    return {
        "status": "cleared",
        "session_id": session_id
    }


# ============================================================================
# NEW: VISUALIZATION ENDPOINT (Does NOT affect existing /ask functionality)
# ============================================================================

@app.post("/api/visualize", response_model=VisualizationResponse)
async def get_visualization(request: VisualizationRequest):
    """
    Get visualization data for a query.
    
    This is a SEPARATE endpoint that does NOT affect the existing /ask endpoint.
    It fetches extended historical data for chart rendering.
    
    Args:
        request: VisualizationRequest with session_id, intent, and params
        
    Returns:
        VisualizationResponse with chart data and configuration
        
    Example:
        POST /api/visualize
        {
            "session_id": "abc123",
            "intent": "annual_metrics",
            "params": {"ticker": "AAPL", "fy": 2023}
        }
        
        Returns:
        {
            "chart_data": {
                "type": "line",
                "period": "annual",
                "data": [...5 years of data...],
                "ticker": "AAPL",
                "target_year": 2023
            },
            "chart_config": {
                "title": "AAPL - Revenue ($B) Trend",
                "x_labels": ["2019", "2020", ...],
                "y_values": [260.17, 274.52, ...],
                ...
            }
        }
    """
    try:
        if not viz_fetcher:
            raise HTTPException(
                status_code=500,
                detail="Visualization fetcher not initialized"
            )
        
        # Check if visualization is applicable
        if not viz_fetcher.should_visualize(request.intent, request.params):
            raise HTTPException(
                status_code=400,
                detail="Visualization not applicable for this query type"
            )
        
        # Fetch visualization data
        chart_data = await viz_fetcher.fetch_viz_data(
            intent=request.intent,
            params=request.params
        )
        
        # Generate chart configuration
        # Smart metric detection from question - detect ALL metrics for combo charts
        question_lower = (request.question or '').lower()
        
        # Detect all metrics in the question
        detected_metrics = []
        metric_map = [
            (['gross margin'], 'gross_margin_pct', 'Gross Margin (%)'),
            (['operating margin'], 'operating_margin_pct', 'Operating Margin (%)'),
            (['net margin', 'profit margin'], 'net_margin_pct', 'Net Margin (%)'),
            (['roe', 'return on equity'], 'roe_pct', 'ROE (%)'),
            (['roa', 'return on assets'], 'roa_pct', 'ROA (%)'),
            (['net income', 'profit'], 'net_income_b', 'Net Income ($B)'),
            (['operating income'], 'op_income_b', 'Operating Income ($B)'),
            (['gross profit'], 'gross_profit_b', 'Gross Profit ($B)'),
            (['revenue', 'sales'], 'revenue_b', 'Revenue ($B)'),
            (['closing price', 'close price', 'closing'], 'close_price', 'Closing Price ($)'),
            (['opening price', 'open price', 'opening'], 'open_price', 'Opening Price ($)'),
            (['high price'], 'high_price', 'High Price ($)'),
            (['low price'], 'low_price', 'Low Price ($)'),
            (['stock price'], 'close_price', 'Stock Price ($)')
        ]
        
        for keywords, field_name, label in metric_map:
            for keyword in keywords:
                if keyword in question_lower:
                    detected_metrics.append((field_name, label))
                    break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_metrics = []
        for metric, label in detected_metrics:
            if metric not in seen:
                seen.add(metric)
                unique_metrics.append((metric, label))
        
        # Use first metric as primary, or default to revenue
        metric_name = unique_metrics[0][0] if unique_metrics else 'revenue_b'
        
        # Pass all detected metrics to chart config generator
        chart_config = viz_fetcher.generate_chart_config(chart_data, metric_name, all_metrics=unique_metrics)
        
        return VisualizationResponse(
            chart_data=chart_data,
            chart_config=chart_config
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Visualization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Visualization generation failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
