from django.http import JsonResponse
import joblib
import pandas as pd
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
model = joblib.load('C:\\Users\\63912\\Desktop\\Agriculture\\data\\prediction.pkl')
df = pd.read_csv(r'C:\\\Users\\63912\\Desktop\\Agriculture\\data\\vegetable_prices.csv')
User = get_user_model()

@api_view(['PUT'])
def update_crop_calendar(request, username, pk):
    try:
        user = CustomUser.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        crop_calendar = Calendar.objects.get(pk=pk, user=user)
    except Calendar.DoesNotExist:
        return Response({'error': 'Crop calendar entry not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CropCalendarSerializer(crop_calendar, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_calendar(request, username, pk):
    try:
        user = CustomUser.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Ensure the calendar entry belongs to the specified user
        calendar = Calendar.objects.get(pk=pk, user=user)
    except Calendar.DoesNotExist:
        return Response({'error': 'Calendar not found or not owned by user'}, status=status.HTTP_404_NOT_FOUND)

    # Perform the deletion
    calendar.delete()
    return Response({
        'message': f'Calendar deleted successfully by {user.username}',
        'deleted_by': user.username
    }, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def create_calendar(request):
    username = request.data.get('username')
    name = request.data.get('name')
    planted_date_str = request.data.get('planted_date')
    harvested_date_str = request.data.get('harvested_date')
    expense = request.data.get('expense')
    earn = request.data.get('earn')


    # Check that all required fields are provided
    if not all([username, name, planted_date_str, harvested_date_str]):
        return Response({'error': 'Username, name, planted date, and harvested date are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the user instance
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid username provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Parse dates
    planted_date = parse_date(planted_date_str)
    harvested_date = parse_date(harvested_date_str)
    if not planted_date or not harvested_date:
        return Response({'error': 'Invalid date format.'}, status=status.HTTP_400_BAD_REQUEST)

    # Convert expense, earn, and profit to integers if provided
    try:
        expense = int(expense) if expense else None
        earn = int(earn) if earn else None

    except ValueError:
        return Response({'error': 'Invalid numerical values.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create the Calendar instance
    calendar = Calendar.objects.create(
        name=name,
        planted_date=planted_date,
        harvested_date=harvested_date,
        expense=expense,
        earn=earn,
        user=user
    )

    return Response({
        'name': calendar.name,
        'planted_date': calendar.planted_date,
        'harvested_date': calendar.harvested_date,
        'expense': calendar.expense,
        'earn': calendar.earn,
        'user': calendar.user.username,
    }, status=status.HTTP_201_CREATED)

def calendar_list_view(request, username):
    user = get_object_or_404(CustomUser, username=username)
    calendars = Calendar.objects.filter(user=user)
    calendar_data = [calendar_to_dict(calendar) for calendar in calendars]
    return JsonResponse(calendar_data, safe=False)

def calendar_to_dict(calendar):
    return {
        'id': calendar.id,
        'name': calendar.name,
        'planted_date': calendar.planted_date,
        'harvested_date': calendar.harvested_date,
        'expense': calendar.expense,
        'user': calendar.user.username,
        'earn': calendar.earn,
    }


@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    brgy = request.data.get('brgy')
    age = request.data.get('age')

    if not all([username, password, first_name, last_name, brgy, age]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        brgy=brgy,
        age=age
    )
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'brgy': user.brgy,
                'age': user.age,
            }
        })
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

def vegetable_monthly_summary_view(request, vegetable_name):
    # Filter the DataFrame for the specified vegetable
    vegetable_df = df[df['Vegetable'] == vegetable_name]

    # Check if vegetable_df is empty
    if vegetable_df.empty:
        return JsonResponse({"error": f"No data available for '{vegetable_name}'"}, status=404)

    # Ensure the 'DATE' column is in datetime format
    vegetable_df['DATE'] = pd.to_datetime(vegetable_df['DATE'])

    # Extract month from 'DATE'
    vegetable_df['Month'] = vegetable_df['DATE'].dt.month

    # Calculate average, peak, and lowest prices for each month
    monthly_stats = vegetable_df.groupby('Month').agg(
        Average_Price=('PRICE', 'mean'),
        Peak_Price=('PRICE', 'max'),
        Lowest_Price=('PRICE', 'min')
    ).reset_index()

    # Add exact dates for Peak and Lowest prices
    monthly_stats['Peak_Date'] = monthly_stats.apply(
        lambda row: vegetable_df.loc[(vegetable_df['Month'] == row['Month']) & 
                                      (vegetable_df['PRICE'] == row['Peak_Price']), 'DATE'].dt.date.iloc[0] 
        if not vegetable_df.loc[(vegetable_df['Month'] == row['Month']) & 
                                (vegetable_df['PRICE'] == row['Peak_Price'])].empty else None, axis=1
    )

    monthly_stats['Lowest_Date'] = monthly_stats.apply(
        lambda row: vegetable_df.loc[(vegetable_df['Month'] == row['Month']) & 
                                      (vegetable_df['PRICE'] == row['Lowest_Price']), 'DATE'].dt.date.iloc[0] 
        if not vegetable_df.loc[(vegetable_df['Month'] == row['Month']) & 
                                (vegetable_df['PRICE'] == row['Lowest_Price'])].empty else None, axis=1
    )

    # Calculate percentage of days with price increases
    monthly_price_increase = vegetable_df.groupby('Month').agg(
        Days_With_Price_Increase=('price_increase', 'sum'),
        Total_Days=('price_increase', 'count')
    ).reset_index()

    # Calculate the percentage
    monthly_price_increase['Percentage_Price_Increase'] = (monthly_price_increase['Days_With_Price_Increase'] /
                                                           monthly_price_increase['Total_Days']) * 100

    # Merge the price stats and price increase percentage
    monthly_stats = pd.merge(monthly_stats, monthly_price_increase[['Month', 'Percentage_Price_Increase']], on='Month')

    # Month number to name mapping
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    # Convert month numbers to names
    monthly_stats['Month'] = monthly_stats['Month'].map(month_names)

    # Sort the DataFrame by month in calendar order
    monthly_stats['Month'] = pd.Categorical(monthly_stats['Month'], categories=list(month_names.values()), ordered=True)
    monthly_stats = monthly_stats.sort_values('Month').reset_index(drop=True)

    # Convert DataFrame to JSON serializable format
    monthly_stats_json = monthly_stats.to_dict(orient='records')

    return JsonResponse(monthly_stats_json, safe=False)





def vegetable_summary_view(request, vegetable_name):
    # Ensure vegetable name is lowercase
    vegetable_name = vegetable_name.lower()

    # Check if the vegetable exists in the DataFrame
    if vegetable_name not in df['Vegetable'].str.lower().unique():
        return JsonResponse({"error": f"No data available for '{vegetable_name}'"}, status=404)

    # Ensure the 'DATE' column is in datetime format
    df['DATE'] = pd.to_datetime(df['DATE'])

    # Group by Vegetable to calculate the required statistics
    vegetable_stats = df.groupby('Vegetable').agg(
        Average_Price=('PRICE', 'mean'),
        Peak_Price=('PRICE', 'max'),
        Lowest_Price=('PRICE', 'min')
    ).reset_index()

    # Find the exact date for the peak price
    peak_dates = df.loc[df.groupby('Vegetable')['PRICE'].idxmax(), ['Vegetable', 'DATE']].rename(columns={'DATE': 'Peak_Price_Date'})

    # Find the exact date for the lowest price
    lowest_dates = df.loc[df.groupby('Vegetable')['PRICE'].idxmin(), ['Vegetable', 'DATE']].rename(columns={'DATE': 'Lowest_Price_Date'})

    # Merge peak and lowest date information into the vegetable statistics DataFrame
    vegetable_stats = vegetable_stats.merge(peak_dates, on='Vegetable')
    vegetable_stats = vegetable_stats.merge(lowest_dates, on='Vegetable')

    # Filter for the specified vegetable
    vegetable_stats = vegetable_stats[vegetable_stats['Vegetable'].str.lower() == vegetable_name]

    # Check if the vegetable has data
    if vegetable_stats.empty:
        return JsonResponse({"error": f"No statistics available for '{vegetable_name}'"}, status=404)

    # Convert the row for the vegetable into a dictionary
    vegetable_data = vegetable_stats.to_dict('records')[0]

    return JsonResponse(vegetable_data)




def predict_and_rank(day, month, year):
    # Get unique vegetable encodings (after encoding the 'Vegetable' column)
    vegetable_encodings = df[['Vegetable', 'Vegetable_Encoded']].drop_duplicates().set_index('Vegetable')['Vegetable_Encoded'].to_dict()
    
    # Prepare future data for prediction
    future_data = pd.DataFrame({
        'Day': [day] * len(vegetable_encodings),
        'Month': [month] * len(vegetable_encodings),
        'Year': [year] * len(vegetable_encodings),
        'Vegetable_Encoded': list(vegetable_encodings.values())
    })
    
    # Ensure there are no NaN values in future_data
    future_data = future_data.ffill()  # Forward fill NaN values if needed
    
    # Make predictions using predict_proba (for classifiers)
    future_probabilities = model.predict_proba(future_data)  # Get probability predictions
    increase_probabilities = future_probabilities[:, 1]  # Probability of price increase (class 1)
    
    # Create DataFrame of predictions
    predictions_df = pd.DataFrame({
        'Vegetable': list(vegetable_encodings.keys()),
        'Increase_Probability': increase_probabilities
    })
    
    # Sort by probability of price increase
    predictions_df = predictions_df.sort_values(by='Increase_Probability', ascending=False).reset_index(drop=True)
    
    # Add rank
    predictions_df['Rank'] = predictions_df.index + 1
    
    # Image URLs (optional)
    image_urls = {
        'Ampalaya': 'https://cdn.pixabay.com/photo/2020/02/23/02/36/green-4872110_640.jpg',      
        'Kamatis': 'https://images.pexels.com/photos/533280/pexels-photo-533280.jpeg?auto=compress&cs=tinysrgb&w=600',
        'Kalabasa': 'https://images.pexels.com/photos/6129264/pexels-photo-6129264.jpeg?auto=compress&cs=tinysrgb&w=600',
        'Pechay': 'https://cdn.pixabay.com/photo/2017/07/11/19/29/bokchoy-2494763_1280.png',
        'Sitao': 'https://images.pexels.com/photos/5352037/pexels-photo-5352037.jpeg?auto=compress&cs=tinysrgb&w=600',
        'Talong': 'https://images.pexels.com/photos/5529949/pexels-photo-5529949.jpeg?auto=compress&cs=tinysrgb&w=600',
        'Mustasa':'https://apps.lsuagcenter.com/NR/rdonlyres/30ECC3E2-80A4-4CEE-8E05-C768FF28450A/93777/Mustard.jpg',
        'Okra': 'https://images.pexels.com/photos/17975554/pexels-photo-17975554/free-photo-of-a-bunch-of-raw-bamia-vegetables.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
        'Upo': 'https://images.pexels.com/photos/18176554/pexels-photo-18176554/free-photo-of-close-up-of-colorful-pumpkins.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
        'Pipino': 'https://images.pexels.com/photos/2329440/pexels-photo-2329440.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    }
    predictions_df['Image'] = predictions_df['Vegetable'].map(image_urls)
    
    # Return the required columns, excluding 'Historical_Mean_Price'
    return predictions_df[['Rank', 'Vegetable', 'Increase_Probability', 'Image']]

# Example view
def predict_view(request, day, month, year):
    ranked_vegetables = predict_and_rank(day, month, year)
    top_10_ranked_vegetables = ranked_vegetables.head(10).to_dict('records')
    
    return JsonResponse({'ranked_vegetables': top_10_ranked_vegetables})
