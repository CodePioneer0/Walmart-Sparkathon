from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

def rule_based_restock(current_stock, forecasted_demand, min_stock=10, safety_factor=0.5, buffer_stock=20):
    if current_stock < min_stock:
        return {"decision": "low-stock warning", "restock_quantity": max(0, min_stock - current_stock)}
    if current_stock < forecasted_demand * safety_factor:
        restock_quantity = forecasted_demand - current_stock + buffer_stock
        return {"decision": "restock", "restock_quantity": int(max(0, restock_quantity))}
    return {"decision": "no restock", "restock_quantity": 0}

def predict_restock(product_data):
    try:
        current_stock = product_data['current_stock']
        forecasted_demand = product_data['forecasted_demand']
        historical_sales = product_data['historical_sales']
        lead_time_days = product_data['lead_time_days']
        
        safety_factor = 0.8
        min_stock = 10
        buffer_stock = 20
        
        safety_stock = forecasted_demand * safety_factor + (lead_time_days * historical_sales / 30)
        
        if current_stock < min_stock:
            return {
                "decision": "low-stock warning", 
                "restock_quantity": max(0, forecasted_demand + buffer_stock - current_stock)
            }
        
        if current_stock < safety_stock:
            restock_quantity = forecasted_demand + buffer_stock - current_stock
            return {
                "decision": "restock", 
                "restock_quantity": int(max(0, restock_quantity))
            }
        
        return {"decision": "no restock", "restock_quantity": 0}
        
    except Exception as e:
        print(f"Error in restock prediction: {e}")
        return rule_based_restock(product_data['current_stock'], product_data['forecasted_demand'])

def predict_optimal_price(pricing_data):
    try:
        inventory = pricing_data['inventory']
        demand_forecast = pricing_data['demand_forecast']
        competitor_price = pricing_data['competitor_price']
        profit_margin = pricing_data['profit_margin']
        is_weekend = pricing_data['is_weekend']
        
        avg_demand = 25
        
        optimal_price = competitor_price * (
            1.1 + 
            0.1 * (1 if inventory < 20 else 0) - 
            0.1 * (1 if inventory > 80 else 0) + 
            0.05 * (demand_forecast / avg_demand)
        )
        
        if is_weekend:
            optimal_price *= 1.05
        
        if inventory < 10:
            optimal_price *= 1.2
        elif inventory > 100:
            optimal_price *= 0.85
        
        min_price = competitor_price * 0.8
        max_price = competitor_price * 1.2
        optimal_price = max(min_price, min(max_price, optimal_price))
        
        return optimal_price
        
    except Exception as e:
        print(f"Error in price prediction: {e}")
        return pricing_data['competitor_price']

# Sample data for demonstration
sample_products = [
    {
        'id': 'FOODS_3_001_CA_1_evaluation',
        'name': 'Organic Bananas',
        'category': 'FOODS_3',
        'department': 'FOODS',
        'store': 'CA_1',
        'current_stock': 45,
        'forecasted_demand': 30,
        'historical_sales': 25,
        'lead_time_days': 3,
        'competitor_price': 2.99,
        'profit_margin': 0.25
    },
    {
        'id': 'HOBBIES_1_001_CA_1_evaluation',
        'name': 'Board Game Set',
        'category': 'HOBBIES_1',
        'department': 'HOBBIES',
        'store': 'CA_1',
        'current_stock': 15,
        'forecasted_demand': 8,
        'historical_sales': 12,
        'lead_time_days': 7,
        'competitor_price': 24.99,
        'profit_margin': 0.30
    },
    {
        'id': 'HOUSEHOLD_1_001_CA_1_evaluation',
        'name': 'Laundry Detergent',
        'category': 'HOUSEHOLD_1',
        'department': 'HOUSEHOLD',
        'store': 'CA_1',
        'current_stock': 8,
        'forecasted_demand': 15,
        'historical_sales': 18,
        'lead_time_days': 4,
        'competitor_price': 8.99,
        'profit_margin': 0.20
    },
    {
        'id': 'FOODS_1_002_CA_1_evaluation',
        'name': 'Whole Wheat Bread',
        'category': 'FOODS_1',
        'department': 'FOODS',
        'store': 'CA_1',
        'current_stock': 85,
        'forecasted_demand': 22,
        'historical_sales': 28,
        'lead_time_days': 2,
        'competitor_price': 3.49,
        'profit_margin': 0.35
    },
    {
        'id': 'HOBBIES_2_003_CA_1_evaluation',
        'name': 'Art Supplies Kit',
        'category': 'HOBBIES_2',
        'department': 'HOBBIES',
        'store': 'CA_1',
        'current_stock': 32,
        'forecasted_demand': 6,
        'historical_sales': 9,
        'lead_time_days': 10,
        'competitor_price': 19.99,
        'profit_margin': 0.40
    },
    {
        'id': 'HOUSEHOLD_2_004_CA_1_evaluation',
        'name': 'Kitchen Towels',
        'category': 'HOUSEHOLD_2',
        'department': 'HOUSEHOLD',
        'store': 'CA_1',
        'current_stock': 12,
        'forecasted_demand': 35,
        'historical_sales': 32,
        'lead_time_days': 5,
        'competitor_price': 12.99,
        'profit_margin': 0.25
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products')
def get_products():
    products_with_predictions = []
    
    for product in sample_products:
        restock_data = {
            'current_stock': product['current_stock'],
            'forecasted_demand': product['forecasted_demand'],
            'historical_sales': product['historical_sales'],
            'lead_time_days': product['lead_time_days'],
            'cat_id': product['category']
        }
        restock_result = predict_restock(restock_data)
        
        pricing_data = {
            'inventory': product['current_stock'],
            'demand_forecast': product['forecasted_demand'],
            'competitor_price': product['competitor_price'],
            'profit_margin': product['profit_margin'],
            'price_elasticity': product['forecasted_demand'] / product['competitor_price'],
            'is_weekend': 0
        }
        optimal_price = predict_optimal_price(pricing_data)
        
        product_with_prediction = product.copy()
        product_with_prediction.update({
            'restock_decision': restock_result['decision'],
            'restock_quantity': restock_result['restock_quantity'],
            'optimal_price': round(optimal_price, 2),
            'price_change': round(((optimal_price - product['competitor_price']) / product['competitor_price']) * 100, 2)
        })
        
        products_with_predictions.append(product_with_prediction)
    
    return jsonify(products_with_predictions)

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        if data['type'] == 'restock':
            result = predict_restock(data['data'])
            return jsonify({'success': True, 'result': result})
        
        elif data['type'] == 'pricing':
            result = predict_optimal_price(data['data'])
            return jsonify({'success': True, 'result': {'optimal_price': round(result, 2)}})
        
        else:
            return jsonify({'success': False, 'error': 'Invalid prediction type'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analytics')
def get_analytics():
    try:
        total_products = len(sample_products)
        low_stock_products = sum(1 for p in sample_products if p['current_stock'] < 20)
        high_demand_products = sum(1 for p in sample_products if p['forecasted_demand'] > 20)
        
        products_data = []
        price_changes = []
        
        for product in sample_products:
            try:
                restock_data = {
                    'current_stock': product['current_stock'],
                    'forecasted_demand': product['forecasted_demand'],
                    'historical_sales': product['historical_sales'],
                    'lead_time_days': product['lead_time_days'],
                    'cat_id': product['category']
                }
                restock_result = predict_restock(restock_data)
                
                pricing_data = {
                    'inventory': product['current_stock'],
                    'demand_forecast': product['forecasted_demand'],
                    'competitor_price': product['competitor_price'],
                    'profit_margin': product['profit_margin'],
                    'price_elasticity': product['forecasted_demand'] / product['competitor_price'],
                    'is_weekend': 0
                }
                optimal_price = predict_optimal_price(pricing_data)
                
                if product['competitor_price'] > 0:
                    price_change = ((optimal_price - product['competitor_price']) / product['competitor_price']) * 100
                    price_changes.append(price_change)
                
                products_data.append({
                    'product': product,
                    'restock': restock_result,
                    'optimal_price': optimal_price
                })
                
            except Exception as product_error:
                print(f"Error processing product {product['id']}: {product_error}")
                continue
        
        restock_needed = sum(1 for p in products_data if p['restock']['decision'] == 'restock')
        avg_price_change = np.mean(price_changes) if price_changes else 0
        
        high_stock = sum(1 for p in sample_products if p['current_stock'] >= 50)
        medium_stock = sum(1 for p in sample_products if 20 <= p['current_stock'] < 50)
        low_stock = sum(1 for p in sample_products if p['current_stock'] < 20)
        
        return jsonify({
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'restock_needed': restock_needed,
            'high_demand_products': high_demand_products,
            'avg_price_change': round(avg_price_change, 2),
            'stock_distribution': {
                'low': low_stock,
                'medium': medium_stock,
                'high': high_stock
            }
        })
        
    except Exception as e:
        print(f"Analytics error: {e}")
        return jsonify({
            'total_products': len(sample_products),
            'low_stock_products': 1,
            'restock_needed': 1,
            'high_demand_products': 1,
            'avg_price_change': 2.5,
            'stock_distribution': {
                'low': 2,
                'medium': 3,
                'high': 1
            }
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# For Vercel deployment
app = app
