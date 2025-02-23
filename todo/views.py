import json
from django.forms import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import Module, CRUD

def module_list(request):
    modules = Module.objects.all()
    return render(request, "module_list.html", {"modules": modules})

def module_detail_ajax(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    records = CRUD.objects.filter(module_type=module)
    return render(request, "module_detail_ajax.html", {"module": module, "records": records})

# def update_record(request, record_id):
#     record = get_object_or_404(CRUD, id=record_id)
#     module = record.module_type

#     if request.method == "POST":
#         new_values = {}
#         for field in module.module_fields.keys():
#             new_values[field] = request.POST.get(field, "")

#         record.values = new_values
#         try:
#             record.clean()  # Validate data
#             record.save()
#             return redirect("module_detail", module_id=module.id)
#         except ValidationError as e:
#             return render(request, "update_record.html", {"record": record, "module": module, "errors": e.messages})

#     return render(request, "update_record.html", {"record": record, "module": module})

# def delete_record(request, record_id):
#     record = get_object_or_404(CRUD, id=record_id)
#     module_id = record.module_type.id
#     record.delete()
#     return redirect("module_detail", module_id=module_id)

def save_record(request, module_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request."}, status=400)

    module = get_object_or_404(Module, id=module_id)
    record_id = request.POST.get("record_id")

    try:
        values = json.loads(request.POST["values"])  # Deserialize JSON data
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid data format."}, status=400)

    # Convert checkbox fields to boolean
    for field, field_type in module.module_fields.items():
        if field in values and field_type == "checkbox":
            values[field] = values[field] in ["true", "True", True]

    try:
        if record_id:  # Update existing record
            record = get_object_or_404(CRUD, id=record_id)

            # Merge new values with existing values instead of overwriting
            record.values = {**record.values, **values}
            record.save()

            return JsonResponse({"message": "Record updated successfully."})

        # Create a new record
        new_record = CRUD.objects.create(module_type=module, values=values)
        return JsonResponse({"message": "Record added successfully.", "id": new_record.id})

    except Exception as e:
        return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)

def delete_record(request, module_id, record_id):
    if request.method == "POST":
        record = get_object_or_404(CRUD, id=record_id)
        record.delete()
        return JsonResponse({"message": "Record deleted successfully."})

    return JsonResponse({"error": "Invalid request."}, status=400)

@csrf_exempt
def add_module(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    module_name = data.get("module_name", "").strip()
    module_fields = data.get("module_fields", "")

    if not module_name or not module_fields:
        return JsonResponse({"error": "Module name and fields are required."}, status=400)

    try:
        parsed_fields = json.loads(module_fields)  # Ensure it's valid JSON

        module = Module.objects.create(module_name=module_name, module_fields=parsed_fields)

        return JsonResponse({
            "id": module.id,
            "module_name": module.module_name,
            "module_fields": parsed_fields
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON structure in module_fields."}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)