from fastapi import APIRouter
from .customer_routes import router as customer_router
from .interaction_routes import router as interaction_router
from .opportunity_routes import router as opportunity_router
from .salesrep_routes import router as salesrep_router
#from .sales import router as sales_router
router = APIRouter()

router.include_router(customer_router)
router.include_router(interaction_router)
router.include_router(opportunity_router)
router.include_router(salesrep_router)
#router.include_router(sales_router)

__all__ = ["router"]